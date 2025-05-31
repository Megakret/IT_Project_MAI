from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent
from tg_bot.keyboards import admin_kb
from tg_bot.routers.role_model_fsm.admin_fsm import *
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_functions import is_admin
from tg_bot.routers.start_handler import handle_cmd_start
from tg_bot.routers.admin_ui.admin_place import router as place_router
from tg_bot.routers.admin_ui.admin_place import init_admin_place_panel
from tg_bot.routers.admin_ui.admin_request import router as request_router
from tg_bot.routers.admin_ui.admin_user_control import router as user_control_router
from tg_bot.routers.admin_ui.admin_user_control import init_user_control_routers
from tg_bot.routers.admin_ui.admin_channel import router as channel_router

import logging
from tg_bot.loggers.admin_logger import admin_log_handler

router = Router()
logger = logging.getLogger(__name__)
logger.addHandler(admin_log_handler)


def init_admin_routers():
    router.include_routers(
        place_router, request_router, user_control_router, channel_router
    )
    init_user_control_routers()
    init_admin_place_panel()


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


@router.message(F.text == "Назад", AdminFSM.user_manipulation_state)
@router.message(F.text == "Назад", AdminFSM.channel_state)
async def go_back_to_manager_menu(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.start_state)
    await message.answer(text="Назад", reply_markup=admin_kb)


@router.message(F.text == "Назад", AdminFSM.start_state)
async def go_back_to_start(message: Message, state: FSMContext, session: AsyncSession):
    await handle_cmd_start(message, state, session)


@router.error()
async def handle_errors(error: ErrorEvent):
    logger.critical("Uncaught error appeared: %s", error.exception, exc_info=True)
