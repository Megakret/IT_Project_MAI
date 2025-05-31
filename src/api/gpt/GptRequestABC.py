from abc import ABC, abstractmethod
from httpx import AsyncClient, Response


class GptReqeustABC(ABC):
    @abstractmethod
    async def request(self, client: AsyncClient, prompt: dict) -> Response:
        pass
