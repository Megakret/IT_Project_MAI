from httpx import AsyncClient, Response
from os import getenv
from dotenv import load_dotenv

class GptRequest:
    def __init__(self):
        self._indentification_key: str = getenv("GPT_INDENTIFICATION")
        self._api_key: str = getenv("GPT_API_KEY")
        self._url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self._headers: dict = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}"
        }

    async def request(self, client: AsyncClient, prompt: dict) -> Response:
        return await client.post(self._url, headers=self._headers, json=prompt)