import unittest
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорты модулей для тестирования
from src.api.geosuggest.geosuggest import Geosuggest

# from src.api.gpt.GptTalker import GptTalker


class TestGeosuggest(unittest.IsolatedAsyncioTestCase):
    async def test_normal_request(self):
        responce = await Geosuggest.request("Метрополис")
        self.assertEqual(len(responce), 5)


if __name__ == "__main__":
    unittest.main()
