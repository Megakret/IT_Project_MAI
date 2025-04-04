
from httpx import AsyncClient, Response
from os import getenv


_indentification_key: str = getenv("GPT_INDENTIFICATION")
_api_key: str = getenv("GPT_API_KEY")
_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
_headers: dict = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {_api_key}"
}

async def request(client: AsyncClient, prompt: dict) -> Response:
    return await client.post(_url, headers=_headers, json=prompt)