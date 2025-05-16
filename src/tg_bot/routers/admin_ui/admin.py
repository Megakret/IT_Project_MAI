from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.keyboards import admin_kb
from tg_bot.routers.role_model_fsm.admin_fsm import *
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_functions import is_admin
from tg_bot.routers.add_place_handler import handle_cmd_start

router = Router()


@router.message(F.text == "Админ панель")
@router.message(Command("admin_menu"))
async def login_into_manager_menu(
    message: Message, state: FSMContext, session: AsyncSession
):
    if await is_admin(session, message.from_user.id):
        await state.set_state(AdminFSM.start_state)
        await message.answer("Вы прошли валидацию", reply_markup=admin_kb)
    else:
        await message.answer("Вы не являетесь админом!")


@router.message(F.text == "Назад", AdminFSM.channel_state)
async def go_back_to_manager_menu(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.start_state)
    await message.answer(text="Назад", reply_markup=admin_kb)


@router.message(F.text == "Назад", AdminFSM.start_state)
async def go_back_to_start(message: Message, state: FSMContext, session: AsyncSession):
    await handle_cmd_start(message, state, session)
