import json
import tempfile
import unittest
from pathlib import Path

from lugar_maps import LugarMaps
from main_datos_maps import run_batch


class FakeScraper:
    output_path = None
    observed_line_counts = []
    closed_count = 0

    def __init__(self, language):
        self.language = language

    def initDriver(self):
        return True

    def scrapearResultados(self, query, maxResults, startIndex, onResult, businessDelay):
        total = min(maxResults, 5)
        for index in range(startIndex, total):
            place = LugarMaps()
            place.keyword = query
            place.categoria = "Dentista"
            place.nombre = f"Negocio {index}"
            place.email = f"contacto{index}@prueba.test"
            onResult(index, place)
            lines = self.output_path.read_text(encoding="utf-8").splitlines()
            self.observed_line_counts.append(len(lines))
        return total

    def registerEmptySearch(self):
        pass

    def resetEmptySearches(self):
        pass

    def endDriver(self):
        type(self).closed_count += 1


class BatchResumeTest(unittest.TestCase):
    def setUp(self):
        FakeScraper.observed_line_counts = []
        FakeScraper.closed_count = 0
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.output = base / "sendEmail.txt"
        self.progress = base / "progress.json"
        self.log = base / "scraper.log"
        FakeScraper.output_path = self.output

    def tearDown(self):
        self.temp.cleanup()

    def test_incremental_block_and_resume(self):
        searches = ["dentistas en Monterrey"]
        stopped = run_batch(
            searches, max_results=5, business_delay=(0, 0), search_delay=(0, 0),
            output_path=self.output, progress_path=self.progress, log_path=self.log,
            restart=True, simulate_block_after=2, scraper_factory=FakeScraper,
        )
        self.assertEqual(stopped, 2)
        self.assertEqual(FakeScraper.observed_line_counts, [1])
        self.assertEqual(len(self.output.read_text(encoding="utf-8").splitlines()), 2)
        state = json.loads(self.progress.read_text(encoding="utf-8"))
        self.assertEqual(state["last_processed_index"], 1)
        self.assertIn("bloqueo simulado", state["stop_reason"])
        self.assertEqual(FakeScraper.closed_count, 1)

        resumed = run_batch(
            searches, max_results=5, business_delay=(0, 0), search_delay=(0, 0),
            output_path=self.output, progress_path=self.progress, log_path=self.log,
            resume=True, scraper_factory=FakeScraper,
        )
        self.assertEqual(resumed, 0)
        lines = self.output.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 5)
        self.assertEqual(len(set(lines)), 5)
        state = json.loads(self.progress.read_text(encoding="utf-8"))
        self.assertEqual(state["completed_searches"], searches)
        self.assertEqual(state["current_search_index"], 1)
        self.assertEqual(FakeScraper.closed_count, 2)
        self.assertIn("Ejecución detenida limpiamente", self.log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
