from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.user_ui.user_fsm import UserFSM
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_places, Place
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED
from tg_bot.utils_and_validators import shorten_message
from config import MAX_DESCRIPTION_VIEWSIZE

router = Router()
PLACES_PER_PAGE = 5
POSTFIX = "real_place"


async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, **kwargs
) -> list[str]:
    place_list: list[Place] = await get_places(session, page, places_per_page)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{shorten_message(x.desc, MAX_DESCRIPTION_VIEWSIZE)}",
        place_list,
    )

    return place_formatted_list


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_formatted_list, "В базе пока нет ни одного места"
)


@router.message(F.text == "Список мест", UserFSM.start_state)
@router.message(Command("place_list"), UserFSM.start_state)
async def show_place_list(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session)


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, UserFSM.start_state)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_next_page(callback, state, session)


@router.callback_query(F.data == PREV_PAGE + POSTFIX, UserFSM.start_state)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_prev_page(callback, state, session)


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX, UserFSM.start_state)
async def indicator(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.indicator_clicked(callback, state, session)
