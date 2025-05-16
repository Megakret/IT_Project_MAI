from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database.db_functions as db


# use it to alter state depending on delete place outcome
class CantDeletePlace(Exception):
    pass


async def start_delete_place_function(message: Message):
    await message.answer("Введите id места: ")


async def delete_place_function(message: Message, session: AsyncSession):
    try:
        place_id: int = int(message.text)
        await db.remove_place(session, place_id)
        await message.answer(f"Место с id {place_id} успешно удалено")
    except ValueError:
        await message.answer("Id должен представлять из себя число")
        raise CantDeletePlace
    except NoResultFound as e:
        print(e)
        await message.answer("Такого места нет в базе")
        raise CantDeletePlace
