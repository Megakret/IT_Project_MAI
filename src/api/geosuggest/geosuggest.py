from os import getenv
from httpx import AsyncClient

from config import GEOSUGGEST_API_KEY
from api.geosuggest.geosuggestresult import GeosuggestResult


class NonPositivePlacesAmountException(Exception):
    pass


class TooManyPlacesException(Exception):
    pass


class Geosuggest:
    # load_dotenv() uncomment when you do local testing. we already are loading dotenv in main.py

    @staticmethod
    def __form_request(text: str, amount: int = 5) -> str:
        if amount > 10:
            raise TooManyPlacesException("At most 10 places is allowed")

        if amount <= 0:
            raise NonPositivePlacesAmountException(
                "Only positive integer amount of places is allowed"
            )

        return f"https://suggest-maps.yandex.ru/v1/suggest?apikey={GEOSUGGEST_API_KEY}&text={text}&highlight=0&types=biz&results={amount}"

    # Gets text to request places and returns GeosuggestResult
    @staticmethod
    async def request(text: str) -> GeosuggestResult:
        async with AsyncClient() as client:
            try:
                return GeosuggestResult(
                    (await client.get(Geosuggest.__form_request(text))).json()[
                        "results"
                    ]
                )
            except KeyError:
                return GeosuggestResult([])
