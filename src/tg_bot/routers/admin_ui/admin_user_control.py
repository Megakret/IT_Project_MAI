from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from tg_bot.keyboards import yes_no_inline, set_role_inline, user_manipulation_admin_kb
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.Paginator import PaginatorService
import database.db_functions as db

router = Router()
PLACES_PER_PAGE_USERS = 5
POSTFIX_USERS = "list_of_users"


def validate_username(tag: str) -> bool:
    return (
        tag.startswith("@")
        and tag.isascii()
        and len(set(" ,.:/!\\\"'?") & set(tag)) == 0
    )


async def get_formatted_list(
    page: int, places_per_page: int, session: AsyncSession, permission: int, **kwargs
) -> list[str]:
    if permission:
        users_list: list[str] = await db.get_users_by_permission(
            session, page, places_per_page, permission
        )
    else:
        users_list: list[str] = await db.get_banned_users(
            session, page, places_per_page
        )
    users_formated = map(lambda x: f"@{x}", users_list)
    return list(users_formated)


paginator_service = PaginatorService(
    POSTFIX_USERS,
    PLACES_PER_PAGE_USERS,
    get_formatted_list,
    "В базе пока нет ни пользователя с заданными правами",
)


@router.message(F.text == "Управление пользователями", AdminFSM.start_state)
async def open_menu(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.user_manipulation_state)
    await message.answer(
        "Вы вошли в меню управления пользователями.",
        reply_markup=user_manipulation_admin_kb,
    )


@router.message(
    F.text == "Список забанненых пользователей", AdminFSM.user_manipulation_state
)
async def show_users(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session, 0)


@router.message(F.text == "Список пользователей", AdminFSM.user_manipulation_state)
async def show_users(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session, 1)


@router.message(F.text == "Список менеджеров", AdminFSM.user_manipulation_state)
async def show_users(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session, 2)


@router.message(F.text == "Список админов", AdminFSM.user_manipulation_state)
async def show_users(message: Message, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator(message, state, session, 3)


@router.message(F.text == "Забанить пользователя", AdminFSM.user_manipulation_state)
async def ban_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите тего пользователя через @ для того, чтобы забанить его.\nДля отмены операции напишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserManipulationFSM.ban_state)


@router.message(UserManipulationFSM.ban_state)
async def input(message: Message, state: FSMContext):
    text = message.text.strip()
    if not validate_username(message.text):
        message.answer("Формат имени пользователя неверен. Для выхода пропишите /exit")
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
    await call.message.answer(
        f"Пользователь {username} забанен.\nХотите ли вы удалить данные о нём?",
        reply_markup=yes_no_inline,
    )
    await state.set_state(UserManipulationFSM.deletion_state)
    await call.answer()


@router.callback_query(F.data == "no", UserManipulationFSM.ban_verify_state)
async def banned_without_deletion(call: CallbackQuery, state: FSMContext):
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


# @router.message(F.text == "Разбанить пользователя", AdminFSM.user_manipulation_state)
# async def unban
