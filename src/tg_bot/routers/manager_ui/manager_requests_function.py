from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.ui_components.TagSelector import TAG_DATA_KEY, TagSelector
from tg_bot.keyboards import yes_no_inline, request_manager_kb, insert_place_tags_kb
import database.db_functions as db


def __form_message_for_manager(answer: db.AddPlaceRequest):
    return f"""
Место: {answer.place_name}
Адрес: {answer.address}
Описание: {answer.description}
Теги: {answer.tags_formatted}
"""


async def show_confirmation_menu(
    message: Message, state: FSMContext, next_state: State
) -> None:
    await message.answer(
        "Вы уверены, что хотите перейти в режим обработки запросов пользователей?",
        reply_markup=yes_no_inline,
    )
    await state.set_state(next_state)


async def handle_yes_command(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    fail_state: State,
    fail_kb: ReplyKeyboardMarkup,
) -> None:
    print("Yes command")
    try:
        result = await db.get_first_request(session)
    except:

        await callback.message.answer(
            "Сейчас нет ни одного запроса, возвращение", reply_markup=fail_kb
        )
        await callback.message.delete()
        await state.set_state(fail_state)
        return
    await callback.message.edit_text(
        __form_message_for_manager(result), reply_markup=request_manager_kb
    )
    await state.set_state(next_state)
    await state.update_data(request_data=result)


async def handle_no_command(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    keyboard: ReplyKeyboardMarkup,
) -> None:
    await callback.message.answer("Переход в гланое меню...", reply_markup=keyboard)
    await callback.message.delete()
    await state.set_state(next_state)


async def handle_accept(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
) -> None:
    await callback.message.edit_text(
        "Вы уверены, что хотите добавить данное место в базу данных?",
        reply_markup=yes_no_inline,
    )
    await state.set_state(next_state)


async def handle_dismiss(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
) -> None:
    await callback.message.edit_text(
        "Вы уверены, что хотите отклонить данный запрос?", reply_markup=yes_no_inline
    )
    await state.set_state(next_state)


async def handle_accept_confirmation_yes(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    fail_state: State,
    fail_kb: ReplyKeyboardMarkup,
):
    place_requested: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await db.add_place(
        session,
        place_requested.place_name,
        place_requested.address,
        place_requested.description,
    )
    await db.add_place_tags(
        session, place_requested.address, place_requested.tags_formatted.split(";")
    )
    await db.delete_request(session, place_requested.id)
    await state.set_state(next_state)
    await handle_yes_command(callback, state, session, next_state, fail_state, fail_kb)


async def handle_accept_confirmation_no(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    place_data = (await state.get_data())["request_data"]
    await callback.message.edit_text(
        __form_message_for_manager(place_data), reply_markup=request_manager_kb
    )
    await state.set_state(next_state)


async def handle_dismiss_confirmation_yes(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    fail_state: State,
    fail_kb: ReplyKeyboardMarkup,
):
    place_requested: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await db.delete_request(session, place_requested.id)
    await state.set_state(next_state)
    await handle_yes_command(callback, state, session, next_state, fail_state, fail_kb)


async def handle_dismiss_confirmation_no(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    fail_state: State,
    fail_kb: ReplyKeyboardMarkup,
):
    place_data = (await state.get_data())["request_data"]
    await callback.message.edit_text(
        __form_message_for_manager(place_data), reply_markup=request_manager_kb
    )
    await state.set_state(next_state)


# Выводит описание с копированием и ждёт до отправления ему исправленного сообщения
async def handle_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    place_requested: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await callback.message.edit_text(
        f"""Вы хотите изменить описание места {place_requested.place_name}
Описание:
<code>{place_requested.description}</code>""",
        parse_mode="HTML",
        reply_markup=yes_no_inline,
    )
    await state.set_state(next_state)
    await state.update_data(message_to_request=callback.message)


async def handle_yes_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
) -> None:
    place: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await callback.message.edit_text(
        f"Старое описание:\n<code>{place.description}</code>\nВведите новое (нажмите на старое, чтобы скопировать)",
        parse_mode="HTML",
    )
    await state.set_state(next_state)


async def handle_no_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
) -> None:
    place_data = (await state.get_data())["request_data"]
    await callback.message.edit_text(
        __form_message_for_manager(place_data), reply_markup=request_manager_kb
    )
    await state.set_state(next_state)


# Выводит сообщение с да/нет на подтверждение нового описания и сохранением места.
# При нажатии нет - в handle_edit
async def handle_new_description(
    message: Message, state: FSMContext, session: AsyncSession, next_state: State
) -> None:
    text = message.text
    await message.delete()
    if not text:
        return
    request_message: Message = (await state.get_data())["message_to_request"]
    place_requested: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await state.update_data(new_desc=text)
    await state.set_state(next_state)
    await request_message.edit_text(
        f"Вы уверены, что хотите изменить описание места {place_requested.place_name}\nНовое описание:\n<code>{text}</code>",
        parse_mode="HTML",
        reply_markup=yes_no_inline,
    )


async def handle_confirm_new_description(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    data = await state.get_data()
    place_requested: db.AddPlaceRequest = data["request_data"]
    new_desc = data["new_desc"]
    place_requested.description = new_desc
    await state.set_state(next_state)
    await callback.message.edit_text(
        __form_message_for_manager(place_requested), reply_markup=request_manager_kb
    )


async def handle_dismiss_new_description(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    await handle_edit(callback, state, session, next_state)


async def handle_edit_tags_start(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    tag_selector: TagSelector,
):
    await tag_selector.show_tag_menu_on_callback(
        callback,
        state,
        keyboard=insert_place_tags_kb,
        start_message="Нажмите на /<tag>, чтобы его добавить. Нажмите на кнопку, когда закончите добавлять теги\n",
    )
    await state.set_state(next_state)


async def handle_tags_complete_button(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    data = await state.get_data()
    tags = data[TAG_DATA_KEY]
    place: db.AddPlaceRequest = data["request_data"]
    place.tags_formatted = ";".join(tags)
    await state.set_state(next_state)
    await callback.message.edit_text(
        __form_message_for_manager(place), reply_markup=request_manager_kb
    )


async def handle_exit(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    keyboard: ReplyKeyboardMarkup,
):
    place: db.AddPlaceRequest = (await state.get_data())["request_data"]
    await db.delay_add_place_request(session, place.id)
    await callback.message.answer("Возвращение в меню...", keyboard=keyboard)
    await callback.message.delete()
    await state.set_state(next_state)
