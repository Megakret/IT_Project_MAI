from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_functions import get_places_with_tag, Place

from tg_bot.routers.user_fsm import UserFSM
from tg_bot.ui_components.Paginator import PaginatorService
from tg_bot.keyboards import (
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
    SHOW_PLACES_BY_TAG,
    show_places_by_tag_kb,
    back_kb,
)
from tg_bot.ui_components.TagSelector import TAG_DATA_KEY, TagSelector
from tg_bot.utils_and_validators import shorten_message
from tg_bot.config import MAX_DESCRIPTION_VIEWSIZE

router = Router()
POSTFIX = "places_by_tag"
PLACES_PER_PAGE = 4


class GetPlaceByTagFSM(StatesGroup):
    selecting_tag = State()
    watch_places = State()


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
        lambda x: f"{x.name}\n{x.address}\n{shorten_message(x.desc, MAX_DESCRIPTION_VIEWSIZE)}",
        places,
    )
    return list(place_formatted_list)


paginator_service = PaginatorService(
    POSTFIX, PLACES_PER_PAGE, get_places_by_tag, "Мест с таким тегом еще нет"
)


@router.message(F.text == "Найти место по тегу", UserFSM.start_state)
@router.message(Command("get_places_by_tag"), UserFSM.start_state)
async def show_tag_menu_handler(message: Message, state: FSMContext):
    await message.answer("Выберите тег для поиска: ", reply_markup=back_kb)
    await tag_selector.show_tag_menu(
        message,
        state,
        keyboard=show_places_by_tag_kb,
        start_message="Чтобы выйти из команды, напишите /exit. Нажмите на тег </tag>, чтобы найти по нему места: \n",
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
            "Что-то пошло не так. Попробуйте заново войти в меню поиска по тегам."
        )
        await callback.answer()
    except NoTagException:
        await callback.answer("Вы не выбрали ни одного тега")
    await state.set_state(GetPlaceByTagFSM.watch_places)


@router.callback_query(F.data == SHOW_PLACES_BY_TAG, UserFSM.start_state)
async def show_places_invalid(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Что-то пошло не так. Попробуйте заново войти в меню поиска по тегам."
    )
    await callback.answer()


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, GetPlaceByTagFSM.watch_places)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.show_next_page(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так. Попробуйте заново войти в меню поиска по тегам.")


@router.callback_query(F.data == PREV_PAGE + POSTFIX, GetPlaceByTagFSM.watch_places)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.show_prev_page(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так. Попробуйте заново войти в меню поиска по тегам.")


@router.callback_query(
    F.data == INDICATOR_CLICKED + POSTFIX, GetPlaceByTagFSM.watch_places
)
async def prev_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag_list: list[str] = data[TAG_DATA_KEY]
        tag: str = tag_list[-1]
        await paginator_service.indicator_clicked(callback, state, session, tag)
    except KeyError as e:
        print(e)
        await callback.answer("Что-то пошло не так. Попробуйте заново войти в меню поиска по тегам.")
