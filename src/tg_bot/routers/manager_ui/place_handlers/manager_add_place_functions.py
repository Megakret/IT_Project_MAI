from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup

from sqlalchemy.ext.asyncio import AsyncSession
from api.geosuggest.place import Place
from tg_bot.keyboards import insert_place_tags_kb, INSERT_PLACE_TAGS_TAG, back_kb
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
)
from tg_bot.ui_components.TagSelector import (
    TagSelector,
    TAG_DATA_KEY,
)
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError


# @router.message(F.text == "Добавить место")
# @router.message(Command("add_place"))
async def add_place_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Введите место для досуга: ", reply_markup=back_kb)


# @router.message(NewPlaceFSM.enter_place)
async def show_suggestions(
    message: Message, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.show_suggestions(message, state)


# manager variation
# @router.callback_query(F.data.contains(KEYBOARD_PREFIX), NewPlaceFSM.choose_place)
async def choose_suggested_place(
    callback: CallbackQuery, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.selected_place(callback, state)
    await callback.message.answer("Введите описание места")


# @router.message(NewPlaceFSM.enter_description)
async def get_description(
    message: Message, state: FSMContext, tag_selector: TagSelector
):
    description: str = message.text
    await state.update_data(description=description)
    await message.answer("Вставьте теги для места")
    await tag_selector.show_tag_menu(
        message,
        state,
        keyboard=insert_place_tags_kb,
        start_message="Нажмите на тег /<tag>, чтобы добавить его к месту\n",
    )


async def generate_final_answer(database_place: db.Place) -> str:
    return "\n".join(
        (
            f"Айди места: {database_place.id}",
            f"Данные о месте: {database_place.name}\n{database_place.address}",
            f"Ваше описание: {database_place.desc}",
        )
    )


async def answer_form_result(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    keyboard: ReplyKeyboardMarkup,
):
    data = await state.get_data()
    place: Place = data["place"]
    tags: set[str] = data.get(TAG_DATA_KEY, None)
    address: str = place.get_info()
    try:
        does_place_exist: bool = await db.is_existing_place(session, address)
        if not does_place_exist:
            await db.add_place(session, place.get_name(), address, data["description"])
        if tags is not None:
            await db.add_place_tags(session, address, tuple(tags))
    except UniqueConstraintError as e:
        print("Already existing place has been tried to add to global list")
        print(e.message)
    try:
        database_place, rating = await db.get_place_with_score(session, address)
        await message.answer(
            await generate_final_answer(database_place),
            reply_markup=keyboard,
        )
    except UniqueConstraintError as e:
        print(e.message)
        await message.answer(
            "Вы уже добавляли это место",
            reply_markup=keyboard,
        )


# @router.callback_query(F.data == INSERT_PLACE_TAGS_TAG, SelectTagsStates.selecting_tag)
async def insert_tags(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    end_keyboard: ReplyKeyboardMarkup,
):
    await answer_form_result(callback.message, state, session, end_keyboard)
    await callback.answer()
