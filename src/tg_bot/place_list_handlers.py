from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.keyboards import generate_page_kb, starter_kb
from tg_bot.ui_components.Paginator import Paginator, PaginatorService
from database.db_functions import get_places, Place

router = Router()
PLACES_PER_PAGE = 5


class NoMorePlacesException(Exception):
    pass


async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, **kwargs
) -> str:
    place_list: list[Place] = await get_places(session, page, places_per_page)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{x.desc}", place_list
    )
    return place_formatted_list


paginator_service = PaginatorService(
    router, "real_place", "place_list", PLACES_PER_PAGE, get_formatted_list
)
