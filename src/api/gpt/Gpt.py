from os import getenv
import json
import httpx
from abc import ABC

class Gpt(ABC):
    _indentification_key = getenv("GPT_INDENTIFICATION")
    _api_key = getenv("GPT_API_KEY")
    _url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    _headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {_api_key}"
    }
    def __init__(self, path_to_prompt: str):
        with open(path_to_prompt) as prompt_input:
            self._prompt: dict = json.load(prompt_input)
        self._prompt["modelUri"] = f"gpt://{Gpt._indentification_key}/yandexgpt-lite"

    def _append_message(self, message: dict) -> None:
        self._prompt["messages"].append(message)

    # returns protected type _RequestContextManager
    async def _request(self) -> httpx.Response:
        async with httpx.AsyncClient() as session:
            return await session.post(Gpt._url, headers=Gpt._headers, json=self._prompt)
    