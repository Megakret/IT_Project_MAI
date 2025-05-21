from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from api.geosuggest.place import Place
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import (
    back_kb,
    update_place_kb,
    update_place_tags_kb,
)
import database.db_functions as db
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector
from tg_bot.ui_components.TagSelector import TagSelector


async def start_update_function(message: Message):
    await message.answer("Введите название места: ", reply_markup=back_kb)


async def show_geosuggest_menu(
    message: Message, state: FSMContext, geosuggest_selector: GeosuggestSelector
):
    await geosuggest_selector.show_suggestions(message, state)


# not used for handlers
async def show_place_info(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    failure_kb: ReplyKeyboardMarkup | None = None,
):
    try:
        print("FUCKDKALSDJAS")
        data = await state.get_data()
        place: Place = data["place"]
        db_place: db.Place = (await db.get_place_with_score(session, place.get_info()))[
            0
        ]
        tags = await session.run_sync(lambda sync_session: db_place.place_tags)
        tags_str_list = list(map(lambda x: x.place_tag, tags))
        print(tags_str_list)
        if tags is not None:
            await message.answer(
                text=f"Название: {db_place.name}\n"
                f"Адрес: {db_place.address}\nОписание: <code>{db_place.desc}</code>\n"
                f"Теги: {", ".join(tags_str_list)}\n",
                reply_markup=update_place_kb,
                parse_mode="html",
            )
            return
        await message.answer(
            text=f"Название: {db_place.name}\n"
            f"Адрес: {db_place.address}\nОписание: <code>{db_place.desc}</code>\n"
            f"Тегов к этому месту еще нет\n",
            reply_markup=update_place_kb,
            parse_mode="html",
        )
    except NoResultFound:
        await message.answer("Такого места нет в базе данных", reply_markup=failure_kb)
        raise PlaceNotFound


# USE IN TRY CATCH WITH PlaceNotFound
async def selected_place(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    geosuggest_selector: GeosuggestSelector,
    failure_kb: ReplyKeyboardMarkup,
):
    await geosuggest_selector.selected_place(callback, state)
    await show_place_info(callback.message, state, session, failure_kb)


async def start_description_enter_function(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое описание места")
    await callback.answer()


# waiting for db
async def enter_description_function(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    description: str = message.text
    data = await state.get_data()
    place: Place = data["place"]
    await db.update_place_description(session, place.get_info(), description)
    await show_place_info(message, state, session)
    await message.answer("Описание успешно отредактировано.")


async def start_tag_selector(
    callback: CallbackQuery, state: FSMContext, tag_selector: TagSelector
):
    await tag_selector.show_tag_menu(
        callback.message,
        state,
        update_place_tags_kb,
        "Нажмите на тег </tag>, чтобы добавить тег\n",
    )
    await callback.answer()


async def update_tags(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    try:
        tag_list: list[str] = data["tag_list"]
        place: Place = data["place"]
        await db.add_place_tags(session, place.get_info(), tuple(tag_list))
        await show_place_info(
            callback.message,
            state,
            session,
        )
        await callback.message.answer("Теги успешно отредактированы")
        await callback.answer()
    except KeyError:
        await callback.answer(
            "Что-то пошло не так. Попробуйте выйти и ввести команду еще раз."
        )
