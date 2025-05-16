from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
import database.db_functions as db
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector
from api.geosuggest.place import Place
from tg_bot.keyboards import back_kb


# invoke by command
async def start_get_place_function(message: Message):
    await message.answer(
        "Чтобы выйти из команды, напишите /exit. Введите название места: ",
        reply_markup=back_kb,
    )


async def enter_place_function(
    message: Message, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.show_suggestions(message, state)


async def place_selected_function(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    geosuggest_selector: GeosuggestSelector,
    end_keyboard: ReplyKeyboardMarkup,
):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data["place"]
    try:
        db_place: db.Place = (await db.get_place_with_score(session, place.get_info()))[
            0
        ]
        await callback.message.answer(
            f"Название места: {db_place.name}\nid места: {db_place.id}",
            reply_markup=end_keyboard,
        )
    except NoResultFound as e:
        print(e)
        await callback.message.answer(
            "Такого места нет в базе", reply_markup=end_keyboard
        )
        await callback.answer()
