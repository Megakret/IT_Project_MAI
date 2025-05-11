from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.keyboards import manager_kb
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerFSM

router = Router()


def validate_manager(UUID: int) -> bool:
    """temporary function that returns True everytime"""
    return True


@router.message(Command("manager_menu"))
async def login_into_manager_menu(message: Message, state: FSMContext):
    if validate_manager(message.from_user.id):
        await state.set_state(ManagerFSM.start_state)
        await message.answer("Вы прошли валидацию", reply_markup=manager_kb)
    else:
        await message.answer("Вы не являетесь менеджером!")
