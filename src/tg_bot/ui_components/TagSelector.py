from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup,
)
from typing import Coroutine

# It's up to script to provide message instruction for tag input
TAGS = {
    "park": "Парк",
    "museum": "Музей",
    "shopping_center": "Торговый центр",
    "for_friends": "Для друзей",
}
TAG_DATA_KEY = "tag_list"


class SelectTagsStates(StatesGroup):
    selecting_tag = State()
    tag_select_finished = State()


def tag_handler_wrapper(tag: str) -> Coroutine:
    async def routine(message: Message, state: FSMContext):
        nonlocal tag
        data: dict[str, any] = await state.get_data()
        tag_list: list[str] = data.get("tag_list", [])
        tag_list.append(tag)
        await state.update_data(tag_list=tag_list)
        await message.answer(f"Вы выбрали тэг: {TAGS[tag]}")

    return routine


def generate_tag_handlers(router: Router) -> None:  # activate in main
    for key in TAGS:
        router.message.register(
            tag_handler_wrapper(key), Command(key), SelectTagsStates.selecting_tag
        )


# @router.message(Command("get_places_by_tag"))
async def show_tag_menu(
    message: Message,
    state: FSMContext,
    keyboard: InlineKeyboardMarkup | None = None,
    start_message: str = "Нажмите на тег </tag>, чтобы найти по нему места: \n",
):
    formed_message: str = start_message
    formed_message += "\n".join(map(lambda x: f"/{x} - {TAGS[x]}", TAGS))
    await state.set_state(SelectTagsStates.selecting_tag)
    await message.answer(formed_message, reply_markup=keyboard)
