from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext


async def message_sender_wrap(sender: SendMessage):
    await sender


async def custom_clear(state: FSMContext):
    data: dict = await state.get_data()
    page = data.get("page", 0)
    await state.clear()
    await state.update_data(page=page)
