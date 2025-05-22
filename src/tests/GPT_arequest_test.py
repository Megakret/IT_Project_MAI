import pytest
from api.gpt.GptRequest import GptRequest
from httpx import AsyncClient
from config import GPT_INDETIFICATION_KEY
import json
from copy import deepcopy


# Most inheretances of GptRequest are in this form
# If this works, then all other work properly


class GptTest(GptRequest):
    with open("src/tests/json/test_prompt.json", encoding="UTF-8") as file:
        __default_prompt: dict = json.load(file)
        __default_prompt["modelUri"] = (
            f"gpt://{GPT_INDETIFICATION_KEY}/yandexgpt-lite/latest"
        )

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptTest.__default_prompt)

    async def test(self, client: AsyncClient, text: str) -> str:
        prompt = deepcopy(self.__prompt)
        prompt["messages"].append({"role": "user", "text": text})
        response = await self.request(client, prompt)
        return response.json()["result"]["alternatives"][0]["message"]["text"]

    async def test_NAC(self, text: str) -> str:
        async with AsyncClient() as client:
            return await self.test(client, text)


@pytest.mark.asyncio
async def test_request_to_gpt():
    requester = GptTest()
    async with AsyncClient() as client:
        responce = await requester.test(client, "Дай топ 5 математических констант")
        assert responce is not None


@pytest.mark.asyncio
async def test_request_to_gpt_NAC():
    requester = GptTest()
    responce = await requester.test_NAC("Дай топ 5 математических констант")
    assert responce is not None
