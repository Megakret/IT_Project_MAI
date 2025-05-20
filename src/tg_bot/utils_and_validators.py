from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.routers.user_fsm import UserFSM
from tg_bot.ui_components.Paginator import Paginator
from tg_bot.tg_exceptions import MessageIsTooLarge


async def message_sender_wrap(sender: SendMessage):
    await sender


async def custom_clear(state: FSMContext):
    data: dict = await state.get_data()
    paginator: Paginator = data.get("paginator", None)
    await state.clear()
    await state.set_state(UserFSM.start_state)
    if not (paginator is None):
        await state.update_data(paginator=paginator)


def shorten_message(message: str, max_size: int):
    if len(message) <= max_size:
        return message
    return message[:max_size].strip() + "..."


# will use after merge
def validate_message_size(message: str, max_size: int):
    if len(message) > max_size:
        raise MessageIsTooLarge(message_size=len(message), max_size=max_size)
    return message
