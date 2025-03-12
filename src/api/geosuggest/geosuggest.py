import requests
from os import getenv
from dotenv import load_dotenv
from geosuggestresult import GeosuggestResult


class NonPositivePlacesAmountException(Exception):
    pass


class TooManyPlacesException(Exception):
    pass


class Geosuggest:
    def __init__(self):
        load_dotenv()
        self.__api_key: str = getenv("GEOSUGGEST_KEY")

    def __form_request(self, text: str, amount: int = 5) -> str:
        if amount > 10:
            raise TooManyPlacesException("At most 10 places is allowed")

        if amount <= 0:
            raise NonPositivePlacesAmountException(
                "Only positive integer amount of places is allowed"
            )

        return f"https://suggest-maps.yandex.ru/v1/suggest?apikey={self.__api_key}&text={text}&highlight=0&types=biz&results={amount}"

    # Gets text to request places and returns GeosuggestResult
    def request(self, text: str) -> GeosuggestResult:
        return GeosuggestResult(
            requests.post(self.__form_request(text)).json()["results"]
        )
