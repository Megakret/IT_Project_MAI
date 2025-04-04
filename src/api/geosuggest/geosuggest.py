from os import getenv
from dotenv import load_dotenv
from api.geosuggest.geosuggestresult import GeosuggestResult
from httpx import AsyncClient


class NonPositivePlacesAmountException(Exception):
    pass


class TooManyPlacesException(Exception):
    pass


class Geosuggest:
    # load_dotenv() uncomment when you do local testing. we already are loading dotenv in main.py
    __api_key: str = getenv("GEOSUGGEST_KEY")

    @staticmethod
    def __form_request(text: str, amount: int = 5) -> str:
        if amount > 10:
            raise TooManyPlacesException("At most 10 places is allowed")

        if amount <= 0:
            raise NonPositivePlacesAmountException(
                "Only positive integer amount of places is allowed"
            )

        return f"https://suggest-maps.yandex.ru/v1/suggest?apikey={Geosuggest.__api_key}&text={text}&highlight=0&types=biz&results={amount}"

    # Gets text to request places and returns GeosuggestResult
    @staticmethod
    async def request(text: str) -> GeosuggestResult:
        async with AsyncClient() as client:
            return GeosuggestResult(
                (await client.get(Geosuggest.__form_request(text))).json()["results"]
            )
