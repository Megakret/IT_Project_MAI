from GptRequest import request, _indentification_key
import json
from copy import deepcopy
from httpx import AsyncClient
import asyncio


class GptTalker:
    with open("src/api/gpt/consultant_prompt.json") as file:
        __default_prompt = json.load(file)
        __default_prompt["modelUri"] = f"gpt://{_indentification_key}/yandexgpt-lite/latest"
    
    def __init__(self):
        self.__prompt = deepcopy(GptTalker.__default_prompt)
    
    async def talk(self, client: AsyncClient,  user_message: str) -> str:
        self.__prompt["messages"].append({"role": "user", "text": user_message})
        response = (await request(client, self.__prompt)).json()
        self.__prompt["messages"].append(response["result"]["alternatives"][0]["message"])
        return response["result"]["alternatives"][0]["message"]["text"]
    
    async def talk_NAC(self, user_message: str) -> str:
        async with AsyncClient() as client:
            return await self.talk(client, user_message)


if __name__ == "__main__":
    async def main():
        from dotenv import load_dotenv
        load_dotenv()
        
        gpt: GptTalker = GptTalker()
        while s := input():
            print(await gpt.talk_NAC(s))
    asyncio.run(main())