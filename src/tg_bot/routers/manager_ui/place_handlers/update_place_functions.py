from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from tg_bot.tg_exceptions import PlaceNotFound
import database.db_functions as db



async def start_update_function(message: Message):
    await message.answer("Введите id места: ")


async def enter_id_function(message: Message, state: FSMContext):
    try:
        place_id: int = int(message.text)
        await message.answer(f"Место с id {place_id} успешно удалено")
    except ValueError:
        await message.answer("Id должен представлять из себя число")
        raise ValueError