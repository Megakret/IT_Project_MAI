from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_functions import is_manager
from tg_bot.keyboards import manager_kb
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerFSM
from tg_bot.routers.start_handler import handle_cmd_start
from tg_bot.routers.manager_ui.manager_place import router as manager_place_router
from tg_bot.routers.manager_ui.manager_place import init_manager_place_panel
from tg_bot.routers.manager_ui.manager_requests import router as manager_requests_router
from tg_bot.routers.manager_ui.manager_channel import router as manager_channel_router

router = Router()


def init_manager_router():
    init_manager_place_panel()
    router.include_router(manager_place_router)
    router.include_router(manager_requests_router)
    router.include_router(manager_channel_router)


@router.message(F.text == "Панель менеджера")
@router.message(Command("manager_menu"))
async def login_into_manager_menu(
    message: Message, state: FSMContext, session: AsyncSession
):
    if await is_manager(session, message.from_user.id):
        await state.set_state(ManagerFSM.start_state)
        await message.answer("Вы прошли валидацию", reply_markup=manager_kb)
    else:
        await message.answer("Вы не являетесь менеджером!")


@router.message(F.text == "Назад", ManagerFSM.channel_state)
async def go_back_to_manager_menu(message: Message, state: FSMContext):
    await state.set_state(ManagerFSM.start_state)
    await message.answer(text="Назад", reply_markup=manager_kb)


@router.message(F.text == "Назад", ManagerFSM.start_state)
async def go_back_to_start(message: Message, state: FSMContext, session: AsyncSession):
    await handle_cmd_start(message, state, session)
