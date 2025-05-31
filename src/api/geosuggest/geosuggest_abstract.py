from abc import ABC, abstractmethod


class GeosuggestABC(ABC):

    @staticmethod
    @abstractmethod
    async def request(text: str):
        pass
