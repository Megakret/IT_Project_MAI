from GptRequest import GptRequest
from httpx import AsyncClient
import json
from copy import deepcopy

class GptCommandGuesser(GptRequest):
    with open("src/api/gpt/command_prompt.json", encoding="UTF-8") as file:
        __default_prompt = json.load(file)
    
    def __init__(self):
        super().__init__()
        self.__prompt = deepcopy(GptCommandGuesser.__default_prompt)
        self.__prompt["modelUri"] = f"gpt://{self._indentification_key}/yandexgpt-lite/latest"

    async def ask_command(self, client: AsyncClient, message: str) -> str:
        self.__prompt["messages"].append({"role": "user", "text": message})
        response = (await self.request(client, self.__prompt)).json()
        return response["result"]["alternatives"][0]["message"]["text"]

    async def ask_command_NAC(self, message: str) -> str:
        async with AsyncClient() as client:
            return await self.ask_command(client, message)

if __name__ == "__main__":
    from dotenv import load_dotenv
    import asyncio
    load_dotenv()
    async def main():
        g = GptCommandGuesser()
        s = input()
        print(await g.ask_command_NAC(s))
    asyncio.run(main())