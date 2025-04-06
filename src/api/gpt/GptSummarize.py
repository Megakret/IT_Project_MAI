from api.gpt.GptRequest import GptRequest
from httpx import AsyncClient
import json
from copy import deepcopy


class GptSummarize(GptRequest):
    def __init__(self):
        super().__init__()
        with open("src/api/gpt/review_prompt.json") as file:
            self.__prompt = json.load(file)
            self.__prompt["modelUri"] = f"gpt://{self._indentification_key}/yandexgpt-lite/latest"

    def __construct_message(reviews: list[str]) -> str:
        s = "Сделай выжимку из данных отзывов о местах:\n\n"
        for i, l in enumerate(reviews):
            s += f"{i + 1}. {l}\n\n"
        return s

    async def summarize(self, client: AsyncClient, reviews: list[str]) -> str:
        prompt = deepcopy(self.__prompt)
        prompt["messages"].append({"role": "user", "text": GptSummarize.__construct_message(reviews)})
        response = await self.request(client, prompt)
        return response.json()["result"]["alternatives"][0]["message"]["text"]

    async def summarize_NAC(self, reviews: list[str]) -> str:
        async with AsyncClient() as client:
            return await self.summarize(client, reviews)
