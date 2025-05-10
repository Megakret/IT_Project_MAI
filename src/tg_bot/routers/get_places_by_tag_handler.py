from typing import Callable, Coroutine
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
from tg_bot.ui_components.TagSelector import (
    TAGS,
    SelectTagsStates,
    show_tag_menu,
)

router = Router()
POSTFIX = "places_by_tag"
PLACES_PER_PAGE = 4


class NoTagException(Exception):
    pass


# async def get_places_by_tag(
#     page: int, places_per_page: int, session: AsyncSession, tag: str
# ) -> map[str]:
#     places: list[Place] = get_places_with_tag(session, tag)
#     place_formatted_list: map[str] = map(
#         lambda x: f"{x.name}\n{x.address}\n{x.desc}", places
#     )
#     return place_formatted_list


# paginator_service = PaginatorService(
#     POSTFIX, PLACES_PER_PAGE, get_places_by_tag, "Мест с таким тегом еще нет"
# )


@router.message(Command("get_places_by_tag"))
async def show_tag_menu_handler(message: Message, state: FSMContext):
    await show_tag_menu(
        message,
        state,
        keyboard=show_places_by_tag_kb,
        start_message="Нажмите на тег </tag>, чтобы найти по нему места: \n",
    )


# TODO: I NEED FUNCTION FOR PAGED PLACE INFORMATION.
@router.callback_query(F.data == SHOW_PLACES_BY_TAG, SelectTagsStates.selecting_tag)
async def show_places(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    try:
        tag = data["tag"]
        if tag is None:
            raise NoTagException
    except KeyError as e:
        await callback.answer(
            "Что-то пошло не так. Попробуйте еще раз ввести команду /get_places_by_tag"
        )
        await callback.answer()
    except NoTagException:
        await callback.answer("Вы не выбрали ни одного тега")
    places: list[Place] = await get_places_with_tag(session, tag)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{x.desc}", places
    )
    if len(places) == 0:
        await callback.answer("Не нашлось мест с таким тегом.")
        return
    await callback.message.answer("----------------\n".join(place_formatted_list))
    await state.update_data(tag=None)
    await callback.answer()


@router.callback_query(F.data == SHOW_PLACES_BY_TAG)
async def show_places_invalid(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Что-то пошло не так. Попробуйте еще раз ввести команду /get_place_by_tag"
    )
    await callback.answer()
