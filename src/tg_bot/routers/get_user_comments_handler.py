from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.user_fsm import UserFSM
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_comments_of_user, Place
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED
from tg_bot.utils_and_validators import shorten_message
from config import MAX_DESCRIPTION_VIEWSIZE

router = Router()
PLACES_PER_PAGE = 4
POSTFIX = "user_comments"


async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, username: str, **kwargs
) -> str:
    place_list: list[tuple[Place, str, int]] = await get_comments_of_user(
        session, page, places_per_page, username
    )
    place_formatted_list: list[str] = []
    for place, comment, score in place_list:
        place_formatted_list.append(
            f"Название: {place.name}\nАдрес: {place.address}\nКомментарий: {comment}\nВаша оценка: {score}"
        )
    return place_formatted_list


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_formatted_list, "Вы не оставляли никаких отзывов"
)


@router.message(F.text == "Список ваших отзывов", UserFSM.start_state)
@router.message(Command("user_comments"), UserFSM.start_state)
async def show_user_place_list(
    message: Message, state: FSMContext, session: AsyncSession
):
    await paginator_service.start_paginator(
        message, state, session, message.from_user.username
    )


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, UserFSM.start_state)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_next_page(
        callback, state, session, callback.from_user.username
    )


@router.callback_query(F.data == PREV_PAGE + POSTFIX, UserFSM.start_state)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_prev_page(
        callback, state, session, callback.from_user.username
    )


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX, UserFSM.start_state)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.indicator_clicked(
        callback, state, session, callback.from_user.username
    )
