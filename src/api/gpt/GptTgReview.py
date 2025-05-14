from api.gpt.GptRequest import GptRequest
import json
from copy import deepcopy
from httpx import AsyncClient


class GptTgReview(GptRequest):
    with open("src/api/gpt/json/tg_reviewer_prompt.json") as file:
        __default_prompt = json.load(file)

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptTgReview.__default_prompt)
        self.__prompt["modelUri"] = (
            f"gpt://{self._indentification_key}/yandexgpt-lite/rc"
        )

    async def summarize_review(self, client: AsyncClient, review: str) -> str:
        self.__prompt["messages"].append({"role": "user", "text": review})
        answer = (await self.request(client, self.__prompt)).json()
        self.__prompt["messages"].pop()
        try:
            return json.loads(answer["result"]["alternatives"][0]["message"]["text"])
        except json.JSONDecodeError:
            return {"error": True}

    async def summarize_review_NAC(self, review: str) -> str:
        async with AsyncClient() as client:
            return await self.summarize_review(client, review)
