from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
import database.db_functions as db
from api.geosuggest.place import Place

# use it to alter state depending on delete place outcome
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector
from tg_bot.keyboards import back_kb


async def start_delete_place_function(message: Message):
    await message.answer("Введите название места: ", reply_markup=back_kb)


async def show_geosuggest_menu(
    message: Message, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.show_suggestions(message, state)


async def delete_place_function(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    geosuggest_selector: GeosuggestSelector,
    end_keyboard: ReplyKeyboardMarkup,
):
    try:
        await geosuggest_selector.selected_place(callback, state)
        data = await state.get_data()
        place: Place = data["place"]
        await db.delete_place_by_address(session, place.get_info())
        await callback.message.answer(
            f"Место {place.get_name()} было удалено.", reply_markup=end_keyboard
        )
    except ValueError as e:
        print(e)
        await callback.message.answer(
            "Такого места нет в базе", reply_markup=end_keyboard
        )
        raise PlaceNotFound
