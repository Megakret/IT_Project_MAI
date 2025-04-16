from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_user_places, UserPlace
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED

router = Router()
PLACES_PER_PAGE = 5
POSTFIX = "user_place"

async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, user_id: int, **kwargs
) -> str:
    place_list: list[UserPlace] = await get_user_places(session, page, places_per_page, user_id)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.fk_place_address}\n{x.score}\n", place_list
    )
    return place_formatted_list


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_formatted_list
)

@router.message(Command("user_place_list"))
async def show_user_place_list(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session, message.from_user.id)


@router.callback_query(F.data == NEXT_PAGE + POSTFIX)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_next_page(callback, state, session, callback.from_user.id)


@router.callback_query(F.data == PREV_PAGE + POSTFIX)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_prev_page(callback, state, session, callback.from_user.id)


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.indicator_clicked(callback, state, session, callback.from_user.id)
