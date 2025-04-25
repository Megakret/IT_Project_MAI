from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from tg_bot.tg_exceptions import NoTextMessageException
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
    PLACE_KEY,
)
from tg_bot.ui_components.Paginator import PaginatorService
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from api.geosuggest.place import Place
from api.gpt.GptSummarize import GptSummarize
from database.db_functions import get_place_with_score
from database.db_functions import Place as db_Place
from tg_bot.keyboards import (
    show_comments_keyboard,
    GET_COMMENTS_TAG,
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
    SUMMARIZE_COMMENTS_TAG,
)
from tg_bot.test_utils.comments.comments_mock import (
    comments_mock
)

router = Router()
POSTFIX = "comments"


class NoPlaceException(Exception):
    pass


class GetPlaceStates(StatesGroup):
    enter_place = State()
    choose_place = State()


async def get_comments_for_paginator(
    page: int, places_per_page: int, address: str
) -> list[str]:
    return comments_mock.get_comments_by_page(page, places_per_page, address)


geosuggest_selector = GeosuggestSelector(GetPlaceStates.choose_place)
paginator_service = PaginatorService(POSTFIX, 5, get_comments_for_paginator)


class NoPlaceInDbException(Exception):
    pass


@router.message(Command("get_place"))
async def get_place_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название места")
    await state.set_state(GetPlaceStates.enter_place)


@router.message(GetPlaceStates.enter_place)
async def enter_place_handler(message: Message, state: FSMContext):
    await geosuggest_selector.show_suggestions(message, state)


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), GetPlaceStates.choose_place)
async def find_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data.get(PLACE_KEY)
    try:
        db_res = await get_place_with_score(session, place.get_info())
        if db_res is None:
            raise NoPlaceInDbException()
        db_place: db_Place = db_res[0]
        score: int = db_res[1]
        if score is None:
            await callback.message.answer(
                f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВы пока не оценили это место",
                reply_markup=show_comments_keyboard,
            )
        else:
            await callback.message.answer(
                f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВаша оценка месту: {score}",
                reply_markup=show_comments_keyboard,
            )
    except NoPlaceInDbException:
        await callback.message.answer(
            "Этого места еще нет в базе, но вы можете его добавить с помощью команды /add_place"
        )


@router.callback_query(F.data == GET_COMMENTS_TAG)
async def show_comments(callback: CallbackQuery, state: FSMContext):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.start_paginator(
            callback.message, state, place.get_info()
        )
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == NEXT_PAGE + POSTFIX)
async def next_page(callback: CallbackQuery, state: FSMContext):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.show_next_page(callback, state, place.get_info())
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == PREV_PAGE + POSTFIX)
async def next_page(callback: CallbackQuery, state: FSMContext):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.show_prev_page(callback, state, place.get_info())
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX)
async def indicator_clicked(callback: CallbackQuery, state: FSMContext):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.indicator_clicked(callback, state, place.get_info())
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == SUMMARIZE_COMMENTS_TAG)
async def summarize_comments(callback: CallbackQuery, state: FSMContext):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await callback.answer("Ожидайте...")
        summarizer = GptSummarize()
        comments = comments_mock.get_all_comments(place.get_info())
        summarization: str = await summarizer.summarize_NAC(comments)
        await callback.message.answer(summarization)
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")
