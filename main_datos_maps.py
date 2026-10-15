# -*- coding: utf-8 -*-
"""Scraper secuencial, incremental y reanudable de Google Maps."""
import argparse
import json
import logging
import os
import random
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from maps_data_scraper import BlockDetected, GoogleMapsDataScraper

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = BASE_DIR.parent / "sendEmail.txt"
DEFAULT_PROGRESS = BASE_DIR / "progress.json"
DEFAULT_LOG = BASE_DIR / "scraper.log"
DEFAULT_MAX_RESULTS = 15
DEFAULT_BUSINESS_DELAY = (2.0, 5.0)
DEFAULT_SEARCH_DELAY = (30.0, 90.0)

NICHE_RULES = (
    ("restaurante", ("restaurante", "restaurant", "cafe", "cafeteria", "bar", "comida", "tacos", "pizza")),
    ("dental", ("dental", "dentista", "odontolog")),
    ("consultorio", ("consultorio", "medico", "clinica", "salud", "doctor")),
    ("abogados", ("abogado", "legal", "juridic")),
    ("contadores", ("contador", "contable", "contabilidad")),
    ("inmobiliaria", ("inmobiliaria", "bienes raices", "real estate")),
    ("gimnasio", ("gimnasio", "gym", "fitness")),
    ("belleza", ("belleza", "estetica", "spa", "unas", "salon de belleza")),
    ("barberia", ("barberia", "barbero", "peluqueria")),
    ("veterinaria", ("veterinaria", "veterinario", "mascotas")),
    ("taller", ("taller", "mecanico", "automotriz", "autopartes")),
    ("construccion", ("construccion", "constructora", "arquitectura", "herreria")),
    ("hotel", ("hotel", "hostal", "hospedaje", "cabana")),
    ("tienda", ("tienda", "comercio", "boutique", "shop")),
    ("escuela", ("escuela", "colegio", "academia", "universidad", "cursos")),
    ("eventos", ("eventos", "quinta", "salon de fiestas", "banquetes")),
    ("psicologia", ("psicolog", "terapia", "terapeuta")),
    ("fotografia", ("fotograf", "photo", "estudio fotografico")),
    ("seguros", ("seguros", "aseguradora", "insurance")),
)


def normalize_text(value):
    value = unicodedata.normalize("NFKD", value or "")
    return "".join(c for c in value if not unicodedata.combining(c)).casefold()


def infer_niche(place):
    searchable = normalize_text(f"{place.keyword} {place.categoria}")
    for niche, terms in NICHE_RULES:
        if any(term in searchable for term in terms):
            return niche
    return "general"


def clean_field(value):
    return " ".join((value or "").replace("|", " ").split())


def read_existing_emails(output_path):
    if not output_path.exists():
        return set()
    emails = set()
    with output_path.open("r", encoding="utf-8") as source:
        for raw_line in source:
            line = raw_line.strip()
            if line and not line.startswith("#"):
                emails.add(line.split("|", 1)[0].strip().casefold())
    return emails


class IncrementalContactWriter:
    """Añade y sincroniza un contacto sin truncar jamás el archivo."""
    def __init__(self, output_path):
        self.path = Path(output_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.known_emails = read_existing_emails(self.path)
        self._needs_newline = self._missing_trailing_newline()

    def _missing_trailing_newline(self):
        if not self.path.exists() or self.path.stat().st_size == 0:
            return False
        with self.path.open("rb") as source:
            source.seek(-1, os.SEEK_END)
            return source.read(1) != b"\n"

    def append(self, place):
        email = (place.email or "").strip().casefold()
        if not email:
            return "without_email"
        if email in self.known_emails:
            return "duplicate"
        business = clean_field(place.nombre)
        if not business:
            return "without_email"
        line = f"{email}|{infer_niche(place)}|{business}|Equipo {business}\n"
        with self.path.open("a", encoding="utf-8") as output:
            if self._needs_newline:
                output.write("\n")
                self._needs_newline = False
            output.write(line)
            output.flush()
            os.fsync(output.fileno())
        self.known_emails.add(email)
        return "saved"


class ProgressStore:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as source:
                return json.load(source)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"No se pudo leer {self.path}: {error}") from error

    def save(self, state):
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as target:
            json.dump(state, target, ensure_ascii=False, indent=2)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, self.path)


@dataclass
class SearchStats:
    reviewed: int = 0
    saved: int = 0
    without_email: int = 0
    duplicates: int = 0


def build_initial_state(searches):
    return {"version": 1, "searches": searches, "completed_searches": [],
            "current_search_index": 0, "current_query": searches[0] if searches else None,
            "last_processed_index": -1, "stop_reason": None}


def choose_resume(saved_state, searches, resume, restart, stdin=None):
    compatible = isinstance(saved_state, dict) and saved_state.get("searches") == searches
    if not compatible or restart:
        return False
    if resume:
        return True
    stdin = stdin or sys.stdin
    if not stdin.isatty():
        return True
    answer = input("Se encontró progreso compatible. ¿Continuar desde el último negocio? [S/n]: ").strip().casefold()
    return answer not in {"n", "no"}


def load_searches(args):
    searches = list(args.search or [])
    if args.search_file:
        with Path(args.search_file).expanduser().open("r", encoding="utf-8") as source:
            searches.extend(line.strip() for line in source if line.strip() and not line.lstrip().startswith("#"))
    return list(dict.fromkeys(searches))


def configure_logging(path):
    logger = logging.getLogger("maps_batch")
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def random_pause(delay_range, logger, label):
    seconds = random.uniform(*delay_range)
    if seconds > 0:
        logger.info("Pausa %s: %.1f s", label, seconds)
        time.sleep(seconds)


def run_batch(searches, language="ES", max_results=DEFAULT_MAX_RESULTS, max_searches=None,
              business_delay=DEFAULT_BUSINESS_DELAY, search_delay=DEFAULT_SEARCH_DELAY,
              output_path=DEFAULT_OUTPUT, progress_path=DEFAULT_PROGRESS, log_path=DEFAULT_LOG,
              resume=False, restart=False, simulate_block_after=None,
              scraper_factory=GoogleMapsDataScraper):
    """Ejecuta secuencialmente. Devuelve 0 o 2 si se detuvo guardando estado."""
    logger = configure_logging(Path(log_path).expanduser().resolve())
    progress = ProgressStore(progress_path)
    saved_state = progress.load()
    if choose_resume(saved_state, searches, resume, restart):
        state = saved_state
        logger.info("Reanudando búsqueda %d, después del índice %d.",
                    state["current_search_index"] + 1, state["last_processed_index"])
    else:
        state = build_initial_state(searches)
        progress.save(state)

    writer = IncrementalContactWriter(output_path)
    first_search = int(state.get("current_search_index", 0))
    pending_indices = list(range(first_search, len(searches)))
    if max_searches is not None:
        pending_indices = pending_indices[:max_searches]
    if not pending_indices:
        logger.info("No hay búsquedas pendientes para esta ejecución.")
        return 0

    scraper = scraper_factory(language)
    processed_this_run = 0
    active_stats = active_started = active_query = None
    reason = None
    try:
        if not scraper.initDriver():
            raise BlockDetected("no se pudo iniciar Chrome/ChromeDriver")
        for run_position, search_index in enumerate(pending_indices):
            query = searches[search_index]
            start_index = (int(state.get("last_processed_index", -1)) + 1
                           if search_index == first_search else 0)
            state.update({"current_search_index": search_index, "current_query": query,
                          "last_processed_index": start_index - 1, "stop_reason": None})
            progress.save(state)
            active_query, active_started, active_stats = query, time.monotonic(), SearchStats()
            logger.info("Búsqueda %d/%d: %s (desde índice %d, máximo %d)",
                        search_index + 1, len(searches), query, start_index, max_results)

            def on_result(result_index, place):
                nonlocal processed_this_run
                status = "without_email" if place is None else writer.append(place)
                active_stats.reviewed += 1
                if status == "saved":
                    active_stats.saved += 1
                    logger.info("  [%d] correo guardado inmediatamente", result_index)
                elif status == "duplicate":
                    active_stats.duplicates += 1
                else:
                    active_stats.without_email += 1
                state["last_processed_index"] = result_index
                progress.save(state)
                processed_this_run += 1
                if simulate_block_after and processed_this_run >= simulate_block_after:
                    raise BlockDetected("bloqueo simulado solicitado por --simulate-block-after")

            found_count = scraper.scrapearResultados(
                query, maxResults=max_results, startIndex=start_index,
                onResult=on_result, businessDelay=business_delay)
            if found_count == 0:
                scraper.registerEmptySearch()
            else:
                scraper.resetEmptySearches()
            completed = state.setdefault("completed_searches", [])
            if query not in completed:
                completed.append(query)
            state.update({"current_search_index": search_index + 1,
                          "current_query": searches[search_index + 1] if search_index + 1 < len(searches) else None,
                          "last_processed_index": -1, "stop_reason": None})
            progress.save(state)
            elapsed = time.monotonic() - active_started
            logger.info("Resumen '%s': revisados=%d, con correo=%d, sin correo=%d, duplicados=%d, tiempo=%.1f s",
                        query, active_stats.reviewed, active_stats.saved,
                        active_stats.without_email, active_stats.duplicates, elapsed)
            active_stats = active_query = None
            if run_position < len(pending_indices) - 1:
                random_pause(search_delay, logger, "entre búsquedas")
        logger.info("Ejecución terminada limpiamente. Contactos en %s", writer.path)
        return 0
    except KeyboardInterrupt:
        reason = "interrupción por Ctrl+C"
    except BlockDetected as error:
        reason = str(error)
    except Exception as error:
        logger.exception("Fallo no esperado")
        reason = f"error no esperado: {error}"
    finally:
        try:
            scraper.endDriver()
        except Exception:
            logger.exception("No se pudo cerrar Chrome limpiamente")

    state["stop_reason"] = reason
    progress.save(state)
    if active_stats is not None:
        elapsed = time.monotonic() - active_started
        logger.info("Resumen parcial '%s': revisados=%d, con correo=%d, sin correo=%d, duplicados=%d, tiempo=%.1f s",
                    active_query, active_stats.reviewed, active_stats.saved,
                    active_stats.without_email, active_stats.duplicates, elapsed)
    logger.warning("Ejecución detenida limpiamente: %s", reason)
    return 2


def non_negative(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("debe ser cero o mayor")
    return number


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("debe ser un entero positivo")
    return number


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Scraper secuencial y reanudable de Google Maps")
    parser.add_argument("--search", action="append", help="búsqueda; se puede repetir")
    parser.add_argument("--search-file", help="TXT con una búsqueda por línea")
    parser.add_argument("--language", choices=("ES", "EN"), default="ES")
    parser.add_argument("--max-results", type=positive_int, default=DEFAULT_MAX_RESULTS)
    parser.add_argument("--max-searches", type=positive_int)
    parser.add_argument("--business-delay-min", type=non_negative, default=DEFAULT_BUSINESS_DELAY[0])
    parser.add_argument("--business-delay-max", type=non_negative, default=DEFAULT_BUSINESS_DELAY[1])
    parser.add_argument("--search-delay-min", type=non_negative, default=DEFAULT_SEARCH_DELAY[0])
    parser.add_argument("--search-delay-max", type=non_negative, default=DEFAULT_SEARCH_DELAY[1])
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--progress", default=str(DEFAULT_PROGRESS))
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--resume", action="store_true", help="reanuda sin preguntar")
    mode.add_argument("--restart", action="store_true", help="reinicia progreso; no borra contactos")
    parser.add_argument("--simulate-block-after", type=positive_int, metavar="N", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    for minimum, maximum, label in (
        (args.business_delay_min, args.business_delay_max, "pausa entre negocios"),
        (args.search_delay_min, args.search_delay_max, "pausa entre búsquedas")):
        if minimum > maximum:
            parser.error(f"el mínimo de {label} no puede exceder el máximo")
    return args


def main(argv=None):
    args = parse_args(argv)
    searches = load_searches(args)
    if not searches:
        print("Indica al menos un --search o --search-file.", file=sys.stderr)
        return 1
    return run_batch(searches, args.language, args.max_results, args.max_searches,
                     (args.business_delay_min, args.business_delay_max),
                     (args.search_delay_min, args.search_delay_max), args.output,
                     args.progress, args.log, args.resume, args.restart,
                     args.simulate_block_after)


if __name__ == "__main__":
    raise SystemExit(main())
