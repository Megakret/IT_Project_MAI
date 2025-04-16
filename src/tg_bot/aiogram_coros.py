from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext
from tg_bot.ui_components.Paginator import Paginator


async def message_sender_wrap(sender: SendMessage):
    await sender


async def custom_clear(state: FSMContext):
    data: dict = await state.get_data()
    paginator: Paginator = data.get("paginator", None)
    await state.clear()
    if not (paginator is None):
        await state.update_data(paginator=paginator)
