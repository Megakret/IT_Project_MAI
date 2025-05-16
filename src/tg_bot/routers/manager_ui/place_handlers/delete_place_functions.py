from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
import database.db_functions as db
# use it to alter state depending on delete place outcome
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import back_kb

async def start_delete_place_function(message: Message):
    await message.answer("Введите id места: ", reply_markup=back_kb)


async def delete_place_function(message: Message, session: AsyncSession, end_keyboard: ReplyKeyboardMarkup):
    try:
        place_id: int = int(message.text)
        await db.remove_place(session, place_id)
        await message.answer(f"Место с id {place_id} успешно удалено", reply_markup=end_keyboard)
    except ValueError:
        await message.answer("Id должен представлять из себя число")
        raise ValueError
    except NoResultFound as e:
        print(e)
        await message.answer("Такого места нет в базе", reply_markup=end_keyboard)
        raise PlaceNotFound
