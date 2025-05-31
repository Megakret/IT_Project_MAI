from api.geosuggest.geosuggest import GeosuggestResult
import database.db_functions as db
from sqlalchemy.ext.asyncio import AsyncSession


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


def parseAddress(places: GeosuggestResult) -> str:
    addres_data: str = places[0].get_info()
    return addres_data


def parseName(places: GeosuggestResult) -> str:
    return places[0].get_name()
