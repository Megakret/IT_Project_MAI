from typing import Callable, Coroutine
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.Paginator import PaginatorService
from database.db_functions import get_places_with_tag, Place
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED, SHOW_PLACES_BY_TAG, show_places_by_tag_kb

router = Router()
POSTFIX = "places_by_tag"
PLACES_PER_PAGE = 4
TAGS = {
    "park": "Парк",
    "museum": "Музей",
    "shopping_center": "Торговый центр",
    "for_friends": "Для друзей",
}
class NoTagException(Exception):
    pass

class GetPlacesByTagStates(StatesGroup):
    selecting_tag = State()
    show_places = State()

def tag_handler_wrapper(tag: str):
    async def routine(message: Message, state: FSMContext):
        nonlocal tag
        await state.update_data(tag=tag)
        await message.answer(f"Вы выбрали тэг: {TAGS[tag]}")

    return routine


def generate_tag_handlers(): #activate in main
    for key in TAGS:
        router.message.register(tag_handler_wrapper(key), Command(key), GetPlacesByTagStates.selecting_tag)


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
async def show_tag_menu(message: Message, state: FSMContext):
    formed_message: str = "Нажмите на тег </tag>, чтобы найти по нему места: \n"
    formed_message += "\n".join(map(lambda x: f"/{x} - {TAGS[x]}", TAGS))
    await state.set_state(GetPlacesByTagStates.selecting_tag)
    await message.answer(formed_message, reply_markup=show_places_by_tag_kb)


# TODO: I NEED FUNCTION FOR PAGED PLACE INFORMATION.
@router.callback_query(F.data == SHOW_PLACES_BY_TAG, GetPlacesByTagStates.selecting_tag)
async def show_places(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        tag = data["tag"]
        if tag is None:
            raise NoTagException
    except KeyError as e:
        await callback.message.answer("Что-то пошло не так. Попробуйте еще раз ввести команду /get_places_by_tag")
    except NoTagException:
        await callback.message.answer("Вы не выбрали ни одного тега")
    places: list[Place] = await get_places_with_tag(session, tag)
    place_formatted_list: map[str] = map(
        lambda x: f"{x.name}\n{x.address}\n{x.desc}", places
    )
    if(len(places) == 0):
        await callback.message.answer("Не нашлось мест с таким тегом.")
        return
    await callback.message.answer("----------------\n".join(place_formatted_list))
    await state.update_data(tag=None)


@router.callback_query(F.data == SHOW_PLACES_BY_TAG)
async def show_places_invalid(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Что-то пошло не так. Попробуйте еще раз ввести команду /get_place_by_tag")



    
