from GptRequest import request, _indentification_key
import asyncio
from httpx import AsyncClient
import json
from copy import deepcopy


__prompt: dict = None
with open("src/api/gpt/review_prompt.json") as file:
    __prompt = json.load(file)
    __prompt["modelUri"] = f"gpt://{_indentification_key}/yandexgpt-lite/latest"

def __construct_message(reviews: list[str]) -> str:
    s = "Сделай выжимку из данных отзывов о местах:\n\n"
    for i, l in enumerate(reviews):
        s += f"{i + 1}. {l}\n\n"
    return s

async def summarize(client: AsyncClient, reviews: list[str]) -> str:
    prompt = deepcopy(__prompt)
    prompt["messages"].append({"role": "user", "text": __construct_message(reviews)})
    response = await request(client, prompt)
    return response.json()["result"]["alternatives"][0]["message"]["text"]

async def summarize_NAC(reviews: list[str]) -> str:
    async with AsyncClient() as client:
        return await summarize(client, reviews)


