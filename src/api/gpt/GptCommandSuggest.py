import json
from copy import deepcopy
from httpx import AsyncClient
from httpx_retries import RetryTransport

from config import GPT_INDETIFICATION_KEY
from api.gpt.GptRequest import GptRequestYandex


class GptCommand(GptRequestYandex):

    with open("src/api/gpt/json/command_prompt.json", encoding="UTF-8") as file:
        __default_prompt = json.load(file)
        __default_prompt["modelUri"] = (
            f"gpt://{GPT_INDETIFICATION_KEY}/yandexgpt-lite/latest"
        )

    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptCommand.__default_prompt)

    async def command(self, client: AsyncClient, user_message: str) -> str:
        self.__prompt["messages"].append({"role": "user", "text": user_message})
        response = (await self.request(client, self.__prompt)).json()
        print(response)
        self.__prompt["messages"].append(
            response["result"]["alternatives"][0]["message"]
        )
        return response["result"]["alternatives"][0]["message"]["text"]

    async def command_NAC(self, user_message: str) -> str:
        async with AsyncClient(transport=RetryTransport()) as client:
            return await self.command(client, user_message)


if __name__ == "__main__":
    import asyncio

    async def main():
        from dotenv import load_dotenv

        load_dotenv()

        gpt: GptCommand = GptCommand()
        async with AsyncClient() as client:
            while s := input():
                print(await gpt.command(client, s))

    asyncio.run(main())
