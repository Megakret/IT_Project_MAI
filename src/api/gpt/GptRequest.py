from httpx import AsyncClient, Response
from os import getenv

from config import GPT_KEY


class GptRequest:
    def __init__(self):
        self._url: str = (
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        )
        self._headers: dict = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {GPT_KEY}",
        }

    async def request(self, client: AsyncClient, prompt: dict) -> Response:
        return await client.post(
            self._url, headers=self._headers, json=prompt, timeout=None
        )
