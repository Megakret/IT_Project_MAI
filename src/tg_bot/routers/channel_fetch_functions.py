from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from aiogram import Router, types
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncio import gather
from json import load, dump

router = Router()
reviewer = GptTgReview()
# temporary start
# valid_channel_path = "src/tg_bot/json/valid_channels.json"
# with open(valid_channel_path, encoding="utf-8") as json_file:
#     valid_channels: list[dict[str, str]] = load(json_file)


# def save_channels():
#     with open(valid_channel_path, "w", encoding="utf-8") as json_file:
#         dump(valid_channels, json_file)


async def add_channel(tag: str, manager_id: int, session: AsyncSession) -> bool:
    print(tag)
    if await check_channel(tag, session):
        return False
    await db.add_channel(session, tag, manager_id)
    return True


async def remove_channel(tag: str, session: AsyncSession) -> bool:
    try:
        await db.delete_channel(session, tag)
    except ValueError as e:
        print(e)
        return False
    return True


async def check_channel(tag: str, session: AsyncSession):
    does_exist = await db.does_channel_exist(session, tag)
    return does_exist


async def get_channels(
    session: AsyncSession, page: int, places_per_page: int
) -> list[dict[str, str]]:
    result = await db.get_paged_channels(session, page, places_per_page)
    return [
        {"tag": channel_username, "manager": manager_username}
        for channel_username, manager_username in result
    ]


# temporary end


def parseAddress(places: GeosuggestResult) -> str:
    addres_data: str = places[0].get_info()
    return addres_data


def parseName(places: GeosuggestResult) -> str:
    return places[0].get_name()


@router.channel_post()
async def fetch_data(message: types.Message, session: AsyncSession) -> None:
    """
    currently in development, only prints to the console, I wait DB for tg posts
    """
    if not await check_channel(message.chat.username, session):
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
    geosuggest = Geosuggest()
    tasks = [geosuggest.request(place) for place in out["place"]]
    print("passed corutine creation")
    places = await gather(*tasks)
    add_tasks = [
        db.add_place(
            session, parseName(places[i]), parseAddress(places[i]), out["review"][i]
        )
        for i in range(len(places))
    ]
    try:
        await gather(*add_tasks)
    except UniqueConstraintError as e:
        print(e.message)