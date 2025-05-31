from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import (
    InlineKeyboardMarkup,
)
from typing import Coroutine

# Put here new tags
TAGS = {
    "park": "Парк",
    "museum": "Музей",
    "shopping_center": "Торговый центр",
    "for_friends": "Для друзей",
}
TAG_DATA_KEY = "tag_set"
LAST_TAG_KEY = "last_tag"


def tag_handler_wrapper(tag: str, message_writing: bool = True) -> Coroutine:
    """Decorator for handling adding tag\n

    Keyword arguments:\n
    tag (str): tag for which handler is created\n
    message_writing (bool): does handler delete messages on add tag command invoked\n
    """

    async def routine(message: Message, state: FSMContext):
        nonlocal tag
        data: dict[str, any] = await state.get_data()
        tag_set: set[str] = data.get(TAG_DATA_KEY, set())
        tag_set.add(tag)
        await state.update_data(last_tag=tag)
        await state.update_data(tag_set=tag_set)
        if message_writing:
            await message.answer(f"Вы выбрали тэг: {TAGS[tag]}")
        else:
            await message.delete()

    return routine


class TagSelector:
    """Class for managing tag adding logic. On selecting tag puts tag in fsmcontext data by key tag_set.\n
    Saves last tag in same data by key last_tag.\n

    Keyword arguments:\n
    selecting_state (State): state in which user adds tags.\n
    router (Router): router to which tag_selector handlers are anchored.\n
    write_messages (bool): does tag selector deletes user messages on tag add.\n
    """

    def __init__(
        self, selecting_state: State, router: Router, write_messages: bool = True
    ):
        self.write_messages = write_messages
        self._selecting_state = selecting_state
        self._generate_tag_handlers(router)

    def _generate_tag_handlers(self, router: Router) -> None:
        for key in TAGS:
            router.message.register(
                tag_handler_wrapper(key, self.write_messages),
                Command(key),
                self._selecting_state,
            )

    async def show_tag_menu(
        self,
        message: Message,
        state_machine: FSMContext,
        keyboard: InlineKeyboardMarkup | None = None,
        start_message: str = "Нажмите на тег </tag>, чтобы найти по нему места: \n",
    ):
        """Shows tag_menu. Changes state to self._selecting_state\n

        Keyword arguments:
        message: message to which bot is answering\n
        state_machine: user FSMContext\n
        keyboard: inline keyboard for tag intro message.\n
        start_message (str): message before tag menu.\n
        """

        formed_message: str = start_message
        formed_message += "\n".join(map(lambda x: f"/{x} - {TAGS[x]}", TAGS))
        await state_machine.set_state(self._selecting_state)
        await state_machine.update_data(**{TAG_DATA_KEY: set()})
        await message.answer(formed_message, reply_markup=keyboard)

    async def show_tag_menu_on_callback(
        self,
        callback: CallbackQuery,
        state_machine: FSMContext,
        keyboard: InlineKeyboardMarkup | None = None,
        start_message: str = "Нажмите на тег </tag>, чтобы найти по нему места: \n",
    ):
        """Shows tag_menu. Changes state to self._selecting_state\n

        Keyword arguments:\n
        callback: callback to which bot is answering\n
        state_machine: user FSMContext\n
        keyboard: inline keyboard for tag intro message.\n
        start_message (str): message before tag menu.\n
        """
        formed_message: str = start_message
        formed_message += "\n".join(map(lambda x: f"/{x} - {TAGS[x]}", TAGS))
        await state_machine.set_state(self._selecting_state)
        await state_machine.update_data(**{TAG_DATA_KEY: set()})
        await callback.message.edit_text(formed_message, reply_markup=keyboard)
