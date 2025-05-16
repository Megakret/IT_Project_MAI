from typing import Callable, Coroutine
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_places_with_tag, Place
from tg_bot.keyboards import (
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
    SHOW_PLACES_BY_TAG,
    show_places_by_tag_kb,
)
from tg_bot.ui_components.TagSelector import TAGS, TAG_DATA_KEY, TagSelector

router = Router()
POSTFIX = "places_by_tag"
PLACES_PER_PAGE = 4


class GetPlaceByTagFSM(StatesGroup):
    selecting_tag = State()


tag_selector = TagSelector(
    selecting_state=GetPlaceByTagFSM.selecting_tag, router=router
)


class NoTagException(Exception):
    pass


async def get_places_by_tag(
    page: int, places_per_page: int, session: AsyncSession, tag: str
) -> list[str]:
    places: list[Place] = await get_places_with_tag(session, tag, page, places_per_page)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{x.desc}", places
    )
    return list(place_formatted_list)


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_places_by_tag, "Мест с таким тегом еще нет"
)


@router.message(F.text == "Найти место по тегу")
@router.message(Command("get_places_by_tag"))
async def show_tag_menu_handler(message: Message, state: FSMContext):
    await tag_selector.show_tag_menu(
        message,
        state,
        keyboard=show_places_by_tag_kb,
        start_message="Нажмите на тег </tag>, чтобы найти по нему места: \n",
    )


@router.callback_query(F.data == SHOW_PLACES_BY_TAG, GetPlaceByTagFSM.selecting_tag)
async def show_places(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    try:
        tag = data[TAG_DATA_KEY][-1]  # TODO: add fliter by multiple tags in db
        if tag is None:
            raise NoTagException
        await paginator_service.start_paginator(callback.message, state, session, tag)
        await callback.answer()
    except KeyError as e:
        await callback.answer(
            "Что-то пошло не так. Попробуйте еще раз ввести команду /get_places_by_tag"
        )
        await callback.answer()
    except NoTagException:
        await callback.answer("Вы не выбрали ни одного тега")
    await state.set_state(None)


@router.callback_query(F.data == SHOW_PLACES_BY_TAG)
async def show_places_invalid(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Что-то пошло не так. Попробуйте еще раз ввести команду /get_place_by_tag"
    )
    await callback.answer()


@router.callback_query(F.data == NEXT_PAGE + POSTFIX)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.show_next_page(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так, попробуйте заново ввести команду")


@router.callback_query(F.data == PREV_PAGE + POSTFIX)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.show_prev_page(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так, попробуйте заново ввести команду")


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.indicator_clicked(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так, попробуйте заново ввести команду")
