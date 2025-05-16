from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import back_kb
import database.db_functions as db


async def start_update_function(message: Message):
    await message.answer("Введите id места: ", reply_markup=back_kb)


# USE IN TRY CATCH WITH ValueError AND PlaceNotFound
async def enter_id_function(message: Message, state: FSMContext, session: AsyncSession):
    try:
        place_id: int = int(message.text)
        does_place_exists = await db.is_existing_place_by_id(session, place_id)
        if not does_place_exists:
            await message.answer("Такого места нет в базе")
            raise PlaceNotFound
        await state.update_data(place_id=place_id)
        await message.answer("Введите новое название места")
    except ValueError:
        await message.answer("Id должен представлять из себя число")
        raise ValueError


async def enter_name_function(message: Message, state: FSMContext):
    await state.update_data(place_name=message.text)
    await message.answer("Введите новое описание места")


# waiting for db
async def enter_description_function(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    end_keyboard: ReplyKeyboardMarkup,
):
    description: str = message.text
    data = await state.get_data()
    print(data["place_id"])
    print(data["place_name"])
    print(description)
    await message.answer(
        "Место успешно отредактировано. Ждем бд...", reply_markup=end_keyboard
    )
