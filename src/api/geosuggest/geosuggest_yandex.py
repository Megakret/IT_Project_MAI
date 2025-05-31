from httpx import AsyncClient
from httpx_retries import RetryTransport

from config import GEOSUGGEST_API_KEY, RETRY_POLICY_TRANSPORT
from api.geosuggest.geosuggestresult import GeosuggestResult
from api.geosuggest.geosuggest_abstract import GeosuggestABC


class NonPositivePlacesAmountException(Exception):
    pass


class TooManyPlacesException(Exception):
    pass


class GeosuggestYandex(GeosuggestABC):

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
        async with AsyncClient(transport=RetryTransport(RETRY_POLICY_TRANSPORT)) as client:
            try:
                return GeosuggestResult(
                    (await client.get(GeosuggestYandex.__form_request(text))).json()[
                        "results"
                    ]
                )
            except KeyError:
                return GeosuggestResult([])
