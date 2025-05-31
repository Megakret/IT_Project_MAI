import json
from httpx import AsyncClient
from httpx_retries import RetryTransport
from copy import deepcopy

from config import GPT_INDETIFICATION_KEY, RETRY_POLICY_TRANSPORT
from api.gpt.GptRequest import GptRequestYandex


class GptSummarize(GptRequestYandex):
    with open("src/api/gpt/json/review_prompt.json", encoding="UTF-8") as file:
        __default_prompt: dict = json.load(file)
        __default_prompt["modelUri"] = (
            f"gpt://{GPT_INDETIFICATION_KEY}/yandexgpt-lite/latest"
        )

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptSummarize.__default_prompt)

    def __construct_message(reviews: list[str]) -> str:
        s = "Сделай выжимку из данных отзывов о местах:\n\n"
        for i, l in enumerate(reviews):
            s += f"{i + 1}. {l}\n\n"
        return s

    async def summarize(self, client: AsyncClient, reviews: list[str]) -> str:
        prompt = deepcopy(self.__prompt)
        prompt["messages"].append(
            {"role": "user", "text": GptSummarize.__construct_message(reviews)}
        )
        response = await self.request(client, prompt)
        return response.json()["result"]["alternatives"][0]["message"]["text"]

    async def summarize_NAC(self, reviews: list[str]) -> str:
        async with AsyncClient(transport=RetryTransport(RETRY_POLICY_TRANSPORT)) as client:
            return await self.summarize(client, reviews)
