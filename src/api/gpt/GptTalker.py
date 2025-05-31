import json
from copy import deepcopy
from httpx import AsyncClient
from httpx_retries import RetryTransport

from config import GPT_INDETIFICATION_KEY, RETRY_POLICY_TRANSPORT
from api.gpt.GptRequest import GptRequestYandex


class GptTalker(GptRequestYandex):

    with open("src/api/gpt/json/consultant_prompt.json", encoding="UTF-8") as file:
        __default_prompt = json.load(file)
        __default_prompt["modelUri"] = (
            f"gpt://{GPT_INDETIFICATION_KEY}/yandexgpt-lite/latest"
        )

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptTalker.__default_prompt)

    async def talk(self, client: AsyncClient, user_message: str) -> str:
        self.__prompt["messages"].append({"role": "user", "text": user_message})
        response = (await self.request(client, self.__prompt)).json()
        self.__prompt["messages"].append(
            response["result"]["alternatives"][0]["message"]
        )
        return response["result"]["alternatives"][0]["message"]["text"]

    async def talk_NAC(self, user_message: str) -> str:
        async with AsyncClient(transport=RetryTransport(RETRY_POLICY_TRANSPORT)) as client:
            return await self.talk(client, user_message)


if __name__ == "__main__":
    import asyncio

    async def main():
        from dotenv import load_dotenv

        load_dotenv()

        gpt: GptTalker = GptTalker()
        async with AsyncClient() as client:
            while s := input():
                print(await gpt.talk(client, s))

    asyncio.run(main())
