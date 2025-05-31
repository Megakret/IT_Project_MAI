import json
from copy import deepcopy
from httpx import AsyncClient
from httpx_retries import RetryTransport

from config import GPT_KEY, GPT_INDETIFICATION_KEY, RETRY_POLICY_TRANSPORT
from api.gpt.GptRequest import GptRequestYandex


class GptRetellingDescription(GptRequestYandex):
    with open(
        "src/api/gpt/json/retelling_description_prompt.json", encoding="utf-8"
    ) as file:
        __default_prompt: dict = json.load(file)
        __default_prompt["modelUri"] = (
            f"gpt://{GPT_INDETIFICATION_KEY}/yandexgpt-lite/latest"
        )

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptRetellingDescription.__default_prompt)

    def __construct_message(description):
        s = "Сделай краткий пересказ следующего описания места:\n\n"
        s += description + "\n"
        return s

    async def retell(self, client: AsyncClient, description: str):
        prompt = deepcopy(self.__prompt)
        prompt["messages"].append(
            {
                "role": "user",
                "text": GptRetellingDescription.__construct_message(description),
            }
        )
        response = await self.request(client, prompt)
        return response.json()["result"]["alternatives"][0]["message"]["text"]

    async def retell_nac(self, description: str):
        async with AsyncClient(transport=RetryTransport(RETRY_POLICY_TRANSPORT)) as client:
            return await self.retell(client, description)
