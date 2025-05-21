from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
)

from tg_bot.keyboards import (
    user_manipulation_admin_kb,
    chose_role_for_paginator_inline,
    back_kb,
)
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.ui_components.Paginator import PaginatorService
import database.db_functions as db

router = Router()
PLACES_PER_PAGE_USERS = 5
POSTFIX_USERS = "list_of_users"


async def get_formatted_list(
    page: int,
    places_per_page: int,
    session: AsyncSession,
    permission: int,
    *args,
    **kwargs,
) -> list[str]:
    if permission:
        users_list: list[str] = await db.get_users_by_permission(
            session, page, places_per_page, permission
        )
    else:
        users_list: list[str] = await db.get_banned_users(
            session, page, places_per_page
        )
    users_formated = map(lambda x: f"`@{x}`", users_list)
    return list(users_formated)


paginator_service = PaginatorService(
    POSTFIX_USERS,
    PLACES_PER_PAGE_USERS,
    get_formatted_list,
    "В базе данных пока нет ни пользователя с заданными правами",
)


@router.message(F.text == "Список пользователей", AdminFSM.user_manipulation_state)
async def show_users_by_permission(
    message: Message, state: FSMContext, session: AsyncSession
):
    await message.answer("Загрузка...", reply_markup=back_kb)
    await message.answer(
        "Выберите роль для показа:", reply_markup=chose_role_for_paginator_inline
    )
    await state.set_state(UserManipulationFSM.choose_role_for_paginator_state)


@router.callback_query(
    F.data == "banned", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 0, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "user", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 1, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "manager", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 2, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "admin", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_admin(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 3, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
