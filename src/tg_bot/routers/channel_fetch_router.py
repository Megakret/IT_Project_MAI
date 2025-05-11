from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from aiogram import Router, types
from asyncio import gather

router = Router()
reviewer = GptTgReview()


def parseAddres(places: GeosuggestResult) -> str:
    addres_data: str = places[0].get_info()
    i = addres_data.index("·")
    return addres_data[i + 2 :]


@router.channel_post()
async def fetch_data(message: types.Message) -> None:
    """
    currently in development, only prints to the console, I wait DB for tg posts
    """
    out: dict = await reviewer.summarize_review_NAC(
        str(message.caption) + str(message.text)
    )
    print(message.caption)
    print("----------------")
    print(message.text)
    if out["error"]:
        print("Message from " + message.chat.full_name + " is not about place")
        return
    print("passed if")
    tasks = [Geosuggest.request(name) for name in out["place"]]
    print("passed corutine creation")
    places = await gather(*tasks)
    print("Names: ", out["place"])
    print("Addreses: ", list(map(parseAddres, places)))
    print("Reviews: ", out["review"])
