from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import Message

from tg_bot.keyboards import user_manipulation_admin_kb
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from tg_bot.routers.admin_ui.user_manipulation.ban_user import router as ban_router
from tg_bot.routers.admin_ui.user_manipulation.unban_user import router as unban_router
from tg_bot.routers.admin_ui.user_manipulation.change_role import router as role_router
from tg_bot.routers.admin_ui.user_manipulation.user_list import router as list_router
from tg_bot.routers.admin_ui.user_manipulation.delete_comments import (
    router as comments_router,
)


router = Router()


def init_user_control_routers():
    router.include_routers(
        ban_router, list_router, unban_router, comments_router, role_router
    )


@router.message(F.text == "Управление пользователями", AdminFSM.start_state)
async def open_menu(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.user_manipulation_state)
    await message.answer(
        "Вы вошли в меню управления пользователями.",
        reply_markup=user_manipulation_admin_kb,
    )


@router.message(Command("exit"), or_f(*UserManipulationFSM.__all_states__))
@router.message(F.text == "Назад", UserManipulationFSM.choose_role_for_paginator_state)
async def exit_to_first_menu(message: Message, state: FSMContext):
    await message.answer(
        "Переход в меню управления пользователями...",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
