from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import database.db_functions as db
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector
from api.geosuggest.place import Place


# invoke by command
async def get_place_function(message: Message):
    await message.answer(
        "Чтобы выйти из команды, напишите /exit. Введите название места: "
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
):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data["place"]
    try:
        db_place: db.Place = (await db.get_place_with_score(session, place.get_info()))[
            0
        ]
        await callback.message.answer(
            f"Название места: {db_place.name}\nid места: {db_place.id}"
        )
    except NoResultFound:
        await callback.message.answer("Такого места нет в базе")
        await callback.answer()
