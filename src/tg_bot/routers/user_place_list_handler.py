from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.user_fsm import UserFSM
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_user_places, Place
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED
from tg_bot.utils_and_validators import shorten_message
from config import MAX_DESCRIPTION_VIEWSIZE

router = Router()
PLACES_PER_PAGE = 4
POSTFIX = "user_place"


async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, user_id: int, **kwargs
) -> str:
    place_list: list[tuple[Place | int | None]] = await get_user_places(
        session, page, places_per_page, user_id
    )
    place_formatted_list: list[str] = []
    for item in place_list:
        place: Place = item[0]
        score: int | None = item[1]

        if score is not None:
            place_formatted_list.append(
                f"Название: {place.name}\nАдрес: {place.address}\nОписание: {shorten_message(place.desc, MAX_DESCRIPTION_VIEWSIZE)}\nВаша оценка: {score}"
            )
        else:
            place_formatted_list.append(
                f"Название: {place.name}\nАдрес: {place.address}\nОписание: {shorten_message(place.desc, MAX_DESCRIPTION_VIEWSIZE)}\nНет оценки"
            )
    return place_formatted_list


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_formatted_list, "Вы не посещали никаких мест"
)


@router.message(F.text == "Список посещённых мест", UserFSM.start_state)
@router.message(Command("user_place_list"), UserFSM.start_state)
async def show_user_place_list(
    message: Message, state: FSMContext, session: AsyncSession
):
    await paginator_service.start_paginator(
        message, state, session, message.from_user.id
    )


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, UserFSM.start_state)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_next_page(
        callback, state, session, callback.from_user.id
    )


@router.callback_query(F.data == PREV_PAGE + POSTFIX, UserFSM.start_state)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_prev_page(
        callback, state, session, callback.from_user.id
    )


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX, UserFSM.start_state)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.indicator_clicked(
        callback, state, session, callback.from_user.id
    )
