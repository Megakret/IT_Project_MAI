from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from aiogram import Router, types
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncio import gather
from json import load, dump

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


async def check_channel(tag: str, session: AsyncSession):
    does_exist = await db.does_channel_exist(session, tag)
    return does_exist


async def remove_channel(tag: str, session: AsyncSession) -> bool:
    try:
        await db.delete_channel(session, tag)
    except ValueError as e:
        print(e)
        return False
    return True


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
