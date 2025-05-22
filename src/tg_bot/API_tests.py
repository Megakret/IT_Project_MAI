import unittest
import dotenv

from src.api.geosuggest.geosuggest import Geosuggest
from src.api.gpt.GptCommandSuggest import GptCommand

dotenv.load_dotenv()


class TestGeosuggest(unittest.IsolatedAsyncioTestCase):

    async def test_normal_request(self):
        responce = await Geosuggest.request("Метрополис")
        self.assertGreater(len(responce), 0)

    async def test_bad_request(self):
        responce = await Geosuggest.request("You can't find anythiidofjas")
        self.assertEqual(len(responce), 0)

    async def test_get_item(self):
        responce = await Geosuggest.request("Метрополис")
        self.assertGreater(len(responce), 0)
        # Fail if __get_item__ throws exception, there we be 5 items
        responce[1]
        self.assertNotEqual(responce[0], responce[1])


class GptCommandTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.__command_gpt = GptCommand()

    async def test_start(self):
        self.assertEqual(await self.__command_gpt.command_NAC("Начать"), "/start")
        self.assertEqual(await self.__command_gpt.command_NAC("начало"), "/start")
        self.assertEqual(
            await self.__command_gpt.command_NAC("выход В глаВное меню"), "/start"
        )
        self.assertEqual(await self.__command_gpt.command_NAC("в начало"), "/start")
