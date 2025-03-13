import requests
from os import getenv
from dotenv import load_dotenv
from geosuggestresult import GeosuggestResult


class NonPositivePlacesAmountException(Exception):
    pass


class TooManyPlacesException(Exception):
    pass


class Geosuggest:
    load_dotenv()
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
    def request(text: str) -> GeosuggestResult:
        return GeosuggestResult(
            requests.get(Geosuggest.__form_request(text)).json()["results"]
        )


if __name__ == "__main__":
    print(Geosuggest.request(input()))
