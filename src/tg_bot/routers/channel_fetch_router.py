from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from aiogram import Router, types
from asyncio import gather
from json import load, dump

router = Router()
reviewer = GptTgReview()
# temporary start
valid_channel_path = "src/tg_bot/json/valid_channels.json"
with open(valid_channel_path, encoding="utf-8") as json_file:
    valid_channels: list[dict[str, str]] = load(json_file)


def save_channels():
    with open(valid_channel_path, "w", encoding="utf-8") as json_file:
        dump(valid_channels, json_file)


def add_channel(tag: str, manager: str) -> bool:
    print(tag)
    if check_channel(tag):
        return False
    valid_channels.append({"tag": tag, "manager": manager})
    save_channels()
    return True


def remove_channel(tag: str) -> bool:
    for i in range(len(valid_channels)):
        if valid_channels[i]["tag"] == tag:
            valid_channels.pop(i)
            return True
    return False


def check_channel(tag: str):
    for channel in valid_channels:
        if channel["tag"] == tag:
            return True
    return False


def get_channels() -> list[dict[str, str]]:
    return valid_channels


# temporary end


def parseAddress(places: GeosuggestResult) -> str:
    addres_data: str = places[0].get_info()
    i = addres_data.index("·")
    return addres_data[i + 2 :]


@router.channel_post()
async def fetch_data(message: types.Message) -> None:
    """
    currently in development, only prints to the console, I wait DB for tg posts
    """
    if not check_channel(f"@{message.chat.username}"):
        print("Message from unwanted channel:", message.chat.username)
        return
    out: dict = await reviewer.summarize_review_NAC(
        str(message.caption) + str(message.text)
    )
    print("Names: ", out["place"])
    print("Reviews: ", out["review"])
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
    print("Addreses: ", list(map(parseAddress, places)))
