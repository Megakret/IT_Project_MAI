from tg_bot.DispatcherHandler import DispatcherHandler
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
)

from tg_bot.keyboards import (
    yes_no_inline,
    set_role_inline,
    set_role_owner_inline,
    user_manipulation_admin_kb,
    chose_role_for_paginator_inline,
    back_kb,
    select_comment_deletion_mode_kb,
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
)
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from tg_bot.routers.admin_ui.user_manipulation.functions import validate_username
from tg_bot.ui_components.Paginator import PaginatorService
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
    PLACE_KEY,
)
import database.db_functions as db

router = Router()
PLACES_PER_PAGE_USERS = 5
COMMENTS_PER_PAGE_FOR_DELETION = 4
POSTFIX_USERS = "list_of_users"
POSTFIX_COMMENTS = "comments_manager"


@router.message(F.text == "Забанить пользователя", AdminFSM.user_manipulation_state)
async def ban_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите имя пользователя человека, которого Вы хотите заблокировать.\nДля выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserManipulationFSM.ban_state)


@router.message(UserManipulationFSM.ban_state)
async def ban_input(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text.strip()
    if text[1:] == message.from_user.username:
        await message.answer("Не стоит себя блокировать.\nДля выхода пропишите /exit")
        return
    if not validate_username(text):
        await message.answer(
            "Формат имени пользователя неверен. Для выхода пропишите /exit"
        )
        return
    if not await db.does_user_exist(session, text[1:]):
        await message.answer(
            f"Пользователь {text} не найден.\nДля выхода пропишите /exit"
        )
        return
    if not await db.is_owner(session, message.from_user.id) and await db.is_admin(
        session, await db.get_id_by_username(session, text[1:])
    ):
        await message.answer(
            f"Только владелец может блокировать админов.\nДля выхода пропишите /exit"
        )
        return
    if await db.is_username_banned(session, text[1:]):
        await message.answer(
            f"Пользователь {text} уже заблокирован.\nДля выхода пропишите /exit"
        )
        return

    await state.set_state(UserManipulationFSM.ban_verify_state)
    await state.set_data({"username": text})
    await message.answer(
        f"Хотите ли Вы забанить пользователя с ником {text}?\nВсе его права будут удалены.",
        reply_markup=yes_no_inline,
    )


@router.callback_query(F.data == "yes", UserManipulationFSM.ban_verify_state)
async def delete_data_of_banned_person_verify(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
):
    username: str = (await state.get_data())["username"]
    try:
        await db.ban_by_username(session, username[1:])
    except:
        await call.message.answer(
            "Вероятно, вы ошиблись в нике пользователя. Попробуйте ещё раз ввести. Для выхода пропишите /exit"
        )
        await state.set_state(UserManipulationFSM.ban_state)
    id = await db.get_id_by_username(session, username[1:])
    await call.message.edit_text(
        f"Пользователь {username} забанен.\nХотите ли вы удалить данные о нём?",
        reply_markup=yes_no_inline,
    )
    await DispatcherHandler.send_message(
        id, "Поздравляем, Вы забанены!", reply_markup=ReplyKeyboardRemove()
    )
    await DispatcherHandler.set_state(id, None)
    await state.set_state(UserManipulationFSM.deletion_state)
    await call.answer()


@router.callback_query(F.data == "no", UserManipulationFSM.ban_verify_state)
async def not_banned(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Пользователь не был забанен. Возвращение в меню",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "yes", UserManipulationFSM.deletion_state)
async def delete_data(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    username: str = (await state.get_data())["username"]
    print(username)
    await db.delete_user_data_by_username(session, username[1:])
    await call.message.answer(
        "Данные пользователя удалены", reply_markup=user_manipulation_admin_kb
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "no", UserManipulationFSM.deletion_state)
async def banned_without_deletion(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Пользователь забанен, но его данные сохранены",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()
