# -*- coding: utf-8 -*-
import html
import os
import random
import re
import shutil
import time
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lugar_maps import LugarMaps


class BlockDetected(RuntimeError):
    """Señal para detenerse ante bloqueo o fallos transitorios repetidos."""


class GoogleMapsDataScraper:
    BLOCK_TEXT = ("unusual traffic", "tráfico inusual", "not a robot", "no soy un robot",
                  "recaptcha", "our systems have detected", "nuestros sistemas han detectado")

    def __init__(self, idioma, maxConsecutiveTimeouts=3, maxEmptySearches=2):
        self.driver = None
        self.consecutiveTimeouts = 0
        self.consecutiveEmptySearches = 0
        self.maxConsecutiveTimeouts = maxConsecutiveTimeouts
        self.maxEmptySearches = maxEmptySearches
        self.configuracion = self.setConfiguracion(idioma)

    def setConfiguracion(self, idioma):
        conf = {"idioma": "--lang=es-ES", "textoEstrellas": "estrellas",
                "textoReviews": "reseñas", "textoDireccion": "Dirección: ",
                "textoWeb": "Sitio web: ", "textoTelefono": "Teléfono: ",
                "textoPlusCode": "Plus Code: ", "textoHorario": "Ocultar el horario de la semana",
                "remplazarHorario": [" Ocultar el horario de la semana", "El horario podría cambiar", "; "]}
        if idioma == "EN":
            conf.update({"idioma": "--lang=en-GB", "textoEstrellas": "stars",
                         "textoReviews": "reviews", "textoDireccion": "Address: ",
                         "textoWeb": "Website: ", "textoTelefono": "Phone: ",
                         "textoPlusCode": "Plus code: ", "textoHorario": "Hide open hours for the week",
                         "remplazarHorario": [". Hide open hours for the week", "Hours might differ", "; "]})
        return conf

    def initDriver(self):
        try:
            options = webdriver.ChromeOptions()
            for argument in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                             "--disable-gpu", "--window-size=1920,1080", "--log-level=3",
                             self.configuracion["idioma"]):
                options.add_argument(argument)
            chrome_binary = self.findChromeBinary()
            if chrome_binary:
                options.binary_location = chrome_binary
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(35)
            self.driver.get("https://www.google.com/maps/")
            self.detectBlock("al abrir Google Maps")
            consent = self.driver.find_elements(By.XPATH, "//*[@aria-label='Aceptar todo' or @aria-label='Accept all']")
            if consent:
                consent[0].click()
            return True
        except BlockDetected:
            raise
        except Exception as error:
            print(f"Error al iniciar Chrome Driver: {error}")
            return False

    def findChromeBinary(self):
        configured = os.environ.get("CHROME_BINARY")
        if configured and os.path.isfile(configured):
            return configured
        for executable in ("google-chrome-stable", "google-chrome"):
            binary = shutil.which(executable)
            if binary:
                return binary
        cached = sorted(Path.home().glob(".cache/selenium/chrome/linux64/*/chrome"),
                        key=lambda path: path.parent.name, reverse=True)
        if cached:
            return str(cached[0])
        for executable in ("chromium", "chromium-browser"):
            binary = shutil.which(executable)
            if binary:
                return binary
        return None

    def detectBlock(self, context=""):
        if not self.driver:
            return
        try:
            content = "\n".join(((self.driver.current_url or "").casefold(),
                                  (self.driver.title or "").casefold(),
                                  (self.driver.find_element(By.TAG_NAME, "body").text or "").casefold()))
            captcha = self.driver.find_elements(
                By.CSS_SELECTOR, "iframe[src*='recaptcha'], iframe[title*='reCAPTCHA'], #captcha-form, .g-recaptcha")
        except WebDriverException as error:
            raise BlockDetected(f"Chrome dejó de responder {context}: {error}") from error
        if captcha or any(text in content for text in self.BLOCK_TEXT):
            raise BlockDetected(f"captcha o tráfico inusual detectado {context}".strip())

    def registerTimeout(self, context):
        self.consecutiveTimeouts += 1
        self.detectBlock(context)
        if self.consecutiveTimeouts >= self.maxConsecutiveTimeouts:
            raise BlockDetected(f"{self.consecutiveTimeouts} timeouts consecutivos {context}")

    def resetTimeouts(self):
        self.consecutiveTimeouts = 0

    def registerEmptySearch(self):
        self.consecutiveEmptySearches += 1
        self.detectBlock("tras resultados vacíos")
        if self.consecutiveEmptySearches >= self.maxEmptySearches:
            raise BlockDetected(f"{self.consecutiveEmptySearches} búsquedas con resultados vacíos consecutivos")

    def resetEmptySearches(self):
        self.consecutiveEmptySearches = 0

    def collectResultUrls(self, query, maxResults):
        try:
            self.driver.get("https://www.google.com/maps/")
            self.detectBlock("antes de buscar")
            input_box = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input#searchboxinput, input[name='q']")))
            input_box.clear()
            input_box.send_keys(query)
            input_box.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.find_elements(By.CSS_SELECTOR, "div[role='feed']")
                or any(h.text.strip() for h in driver.find_elements(By.TAG_NAME, "h1")))
            self.resetTimeouts()
        except TimeoutException:
            self.registerTimeout(f"al cargar la búsqueda '{query}'")
            return []
        self.detectBlock(f"en la búsqueda '{query}'")
        feeds = self.driver.find_elements(By.CSS_SELECTOR, "div[role='feed']")
        urls, seen = [], set()
        if feeds:
            feed, unchanged_rounds = feeds[0], 0
            while len(urls) < maxResults and unchanged_rounds < 4:
                before = len(urls)
                for link in feed.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']"):
                    href = link.get_attribute("href")
                    canonical = href.split("?")[0] if href else ""
                    if canonical and canonical not in seen:
                        seen.add(canonical)
                        urls.append(href)
                        if len(urls) >= maxResults:
                            break
                unchanged_rounds = unchanged_rounds + 1 if len(urls) == before else 0
                if len(urls) < maxResults:
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    time.sleep(2)
                    self.detectBlock("al desplazar resultados")
        elif any(h.text.strip() for h in self.driver.find_elements(By.TAG_NAME, "h1")):
            urls.append(self.driver.current_url)
        return urls[:maxResults]

    def scrapearResultados(self, kw, maxResults=15, startIndex=0, onResult=None,
                           businessDelay=(2.0, 5.0)):
        urls = self.collectResultUrls(kw, maxResults)
        for index in range(startIndex, len(urls)):
            if index > startIndex:
                delay = random.uniform(*businessDelay)
                if delay > 0:
                    time.sleep(delay)
            place = self.scrapearDatos(kw, url=urls[index])
            if onResult:
                onResult(index, place)
        return len(urls)

    def scrapearDatos(self, kw, url=None):
        place = LugarMaps()
        place.keyword = kw
        try:
            if url:
                self.driver.get(url)
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))
            self.detectBlock("al abrir un negocio")
            self.resetTimeouts()
        except TimeoutException:
            self.registerTimeout("al abrir negocios")
            return None
        try:
            place.nombre = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
            place.estrellas, place.resenas = self.getValoraciones()
            place.categoria = self.buscar_xpath('//button[contains(@jsaction, "pane.") and contains(@jsaction, ".category")]')
            place.direccion = self.getAriaValue("textoDireccion")
            try:
                prefix = self.configuracion["textoWeb"]
                element = self.driver.find_element(By.XPATH, f'//*[contains(@aria-label, "{prefix}")]')
                label = element.get_attribute("aria-label") or ""
                place.web = element.get_attribute("href") or label.replace(prefix, "").strip()
            except Exception:
                place.web = ""
            place.telefono = self.getAriaValue("textoTelefono")
            place.pluscode = self.getAriaValue("textoPlusCode")
            place.horario = self.getHorario()
            place.email = self.findPublicEmail(place.web)
            return place
        except BlockDetected:
            raise
        except Exception as error:
            print(f"No se pudo leer el negocio: {error}")
            return None

    def getAriaValue(self, key):
        prefix = self.configuracion[key]
        try:
            label = self.driver.find_element(By.XPATH, f'//*[contains(@aria-label, "{prefix}")]').get_attribute("aria-label")
            return (label or "").replace(prefix, "").strip()
        except Exception:
            return ""

    def findPublicEmail(self, website):
        if not website:
            return ""
        website = unquote(website.strip())
        if not website.startswith(("http://", "https://")):
            website = "https://" + website
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"})

        def fetch(url):
            try:
                response = session.get(url, timeout=10, allow_redirects=True)
                response.raise_for_status()
                if "text/html" not in response.headers.get("content-type", "").lower():
                    return "", url
                return response.text[:2_000_000], response.url
            except requests.RequestException:
                return "", url

        homepage, final_url = fetch(website)
        if not homepage:
            return ""
        pages = [(homepage, final_url)]
        base_host = urlparse(final_url).netloc.casefold().removeprefix("www.")
        for match in re.finditer(r"href\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]", homepage, re.I):
            candidate = urljoin(final_url, html.unescape(match.group(1)).strip())
            parsed = urlparse(candidate)
            host = parsed.netloc.casefold().removeprefix("www.")
            if host != base_host or not any(term in (parsed.path + parsed.query).casefold()
                                            for term in ("contact", "contacto", "nosotros", "about")):
                continue
            if candidate == final_url or any(url == candidate for _, url in pages):
                continue
            page_text, resolved = fetch(candidate)
            if page_text:
                pages.append((page_text, resolved))
            if len(pages) >= 4:
                break
        pattern = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,24}", re.I)
        blocked = ("example.com", "email.com", "domain.com", "sentry.io", "wixpress.com",
                   "wordpress.org", "google.com", "cloudflare.com", "schema.org", "noreply@", "no-reply@")
        emails = set()
        for page_text, _ in pages:
            decoded = html.unescape(unquote(page_text))
            decoded = re.sub(r"\s*[\[(]at[\])]\s*", "@", decoded, flags=re.I)
            for email in pattern.findall(decoded):
                cleaned = email.strip(". ,;:()[]{}<>\"").casefold()
                if not any(part in cleaned for part in blocked) and not cleaned.endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                    emails.add(cleaned)
        if not emails:
            return ""
        domain_matches = [email for email in emails if email.rsplit("@", 1)[-1].endswith(base_host)]
        preferred = domain_matches or list(emails)
        return sorted(preferred, key=lambda email: (not email.startswith(("contact", "info", "hola", "ventas")), email))[0]

    def getValoraciones(self):
        labels = [e.get_attribute("aria-label") or "" for e in self.driver.find_elements(
            By.CSS_SELECTOR, "[role='img'][aria-label]")]
        for label in labels:
            rating = re.search(rf"([\d.,]+)\s*{re.escape(self.configuracion['textoEstrellas'])}", label, re.I)
            if rating:
                reviews = re.search(rf"([\d.,]+)\s*{re.escape(self.configuracion['textoReviews'])}", label, re.I)
                return rating.group(1), reviews.group(1) if reviews else ""
        return "", ""

    def buscar_xpath(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath).text
        except Exception:
            return ""

    def getHorario(self):
        try:
            prefix = self.configuracion["textoHorario"]
            schedule = self.driver.find_element(By.XPATH, f'//*[contains(@aria-label, "{prefix}")]').get_attribute("aria-label")
            for old, new in zip(self.configuracion["remplazarHorario"], ("", "", "\n")):
                schedule = schedule.replace(old, new)
            return schedule
        except Exception:
            return ""

    def endDriver(self):
        if self.driver:
            try:
                self.driver.quit()
            finally:
                self.driver = None
