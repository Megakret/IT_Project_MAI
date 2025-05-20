from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from api.geosuggest.place import Place
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import back_kb
import database.db_functions as db
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector


async def start_update_function(message: Message):
    await message.answer("Введите название места: ", reply_markup=back_kb)


async def show_geosuggest_menu(
    message: Message, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.show_suggestions(message, state)


# USE IN TRY CATCH WITH PlaceNotFound
async def selected_place(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    geosuggest_selector: GeosuggestSelector,
    failure_kb: ReplyKeyboardMarkup,
):
    try:
        await geosuggest_selector.selected_place(callback, state)
        data = await state.get_data()
        place: Place = data["place"]
        place_exists = await db.is_existing_place(session, place.get_info())
        if not place_exists:
            raise ValueError
        await callback.message.answer("Введите новое описание места")
    except ValueError:
        await callback.message.answer(
            "Такого места нет в базе", reply_markup=failure_kb
        )
        raise PlaceNotFound


# waiting for db
async def enter_description_function(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    end_keyboard: ReplyKeyboardMarkup,
):
    description: str = message.text
    data = await state.get_data()
    place: Place = data["place"]
    print(place.get_info())
    print(description)
    await message.answer(
        "Место успешно отредактировано. Ждем бд...", reply_markup=end_keyboard
    )
