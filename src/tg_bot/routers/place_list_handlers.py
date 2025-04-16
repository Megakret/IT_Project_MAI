from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_places, Place
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED

router = Router()
PLACES_PER_PAGE = 5
POSTFIX = "real_place"

async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, **kwargs
) -> str:
    place_list: list[Place] = await get_places(session, page, places_per_page)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{x.desc}", place_list
    )
    return place_formatted_list


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_formatted_list
)

@router.message(Command("place_list"))
async def show_place_list(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session)

@router.callback_query(F.data == NEXT_PAGE + POSTFIX)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_next_page(callback, state, session)


@router.callback_query(F.data == PREV_PAGE + POSTFIX)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.show_prev_page(callback, state, session)


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX)
async def indicator(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.indicator_clicked(callback, state, session)
