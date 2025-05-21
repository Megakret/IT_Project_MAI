from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

from tg_bot.keyboards import user_manipulation_admin_kb
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.admin_ui.user_manipulation.user_list import paginator_service
from tg_bot.routers.admin_ui.user_manipulation.functions import validate_username
import database.db_functions as db


router = Router()


@router.message(F.text == "Разбанить пользователя", AdminFSM.user_manipulation_state)
async def unban(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Введите имя пользователя, которого вы хотите разблокировать.\nДля выходи пропишите /exit\nСписок заблокированных пользователей:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await paginator_service.start_paginator(
        message, state, session, 0, parse_mode="MARKDOWN"
    )
    await state.set_state(UserManipulationFSM.unban_name_input_state)


@router.message(UserManipulationFSM.unban_name_input_state)
async def unban_person(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text.strip()
    if not validate_username(text):
        await message.answer("Неправильный формат имени, для выходи пропишите /exit")
        return
    if not await db.is_username_banned(session, text[1:]):
        await message.answer(
            f"Пользователь {text} либо не заблокирован, либо не существует"
        )
        return
    await db.unban_by_username(session, message.text[1:])
    await message.answer(
        f"Пользователь {text} разблокирован",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
