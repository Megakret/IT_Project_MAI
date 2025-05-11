from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.keyboards import manager_kb
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerFSM
from tg_bot.routers.add_place_handler import handle_cmd_start
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.routers.add_place_handler import get_permisions

router = Router()


def validate_manager(username: str) -> bool:
    return get_permisions(username)


@router.message(F.text == "Панель менеджера")
@router.message(Command("manager_menu"))
async def login_into_manager_menu(message: Message, state: FSMContext):
    if validate_manager(message.from_user.username):
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
