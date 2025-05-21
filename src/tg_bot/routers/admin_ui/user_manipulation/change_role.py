from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
)
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards import (
    set_role_inline,
    set_role_owner_inline,
    user_manipulation_admin_kb,
)
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM

from tg_bot.routers.admin_ui.user_manipulation.functions import validate_username
import database.db_functions as db

router = Router()
PLACES_PER_PAGE_USERS = 5
COMMENTS_PER_PAGE_FOR_DELETION = 4
POSTFIX_USERS = "list_of_users"
POSTFIX_COMMENTS = "comments_manager"


@router.message(
    F.text == "Изменить роль пользователя", AdminFSM.user_manipulation_state
)
async def change_role(message: Message, state: FSMContext):
    await message.answer(
        "Введите имя пользователя через @\nДля выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserManipulationFSM.change_role_state)


@router.message(UserManipulationFSM.change_role_state)
async def change_role_input_name(
    message: Message, state: FSMContext, session: AsyncSession
):
    if message.text[1:] == message.from_user.username:
        await message.answer(
            "Вы не можете изменить свою собственную роль!\nДля выхода пропишите /exit"
        )
        return
    if not validate_username(message.text):
        await message.answer(
            f"Неверный формат имени: `{message.text}`. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    if not (await db.does_user_exist(session, message.text[1:])):
        await message.answer(
            f"Пользователь `{message.text}` не существует. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    if await db.is_username_banned(session, message.text[1:]):
        await message.answer(
            f"Пользователь `{message.text}` заблокирован. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    is_it_owner = await db.is_owner(session, message.from_user.id)
    is_targert_admin = await db.is_admin(
        session, await db.get_id_by_username(session, message.text[1:])
    )
    if not is_it_owner and is_targert_admin:
        await message.answer(
            "Только владельцы могут менять роли админов! Для выхода пропишите /exit"
        )
        return
    if is_it_owner:
        await message.answer("Выберите роль:", reply_markup=set_role_owner_inline)
        await state.update_data({"is_owner": True, "username": message.text})
        await state.set_state(UserManipulationFSM.select_role_state)
    else:
        await message.answer("Выберите роль:", reply_markup=set_role_inline)
        await state.update_data({"is_owner": False, "username": message.text})
        await state.set_state(UserManipulationFSM.select_role_state)


@router.callback_query(F.data == "user", UserManipulationFSM.select_role_state)
async def set_user(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await db.make_user(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Пользователь"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "manager", UserManipulationFSM.select_role_state)
async def set_manager(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await db.make_manager(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Менеджер"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "admin", UserManipulationFSM.select_role_state)
async def set_admin(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if not data["is_owner"]:
        await call.message.answer("А твикать коллбеки не красиво, ничего не получилось")
        return
    await db.make_admin(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Админ"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()
