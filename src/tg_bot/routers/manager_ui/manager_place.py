from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.keyboards import manager_kb
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerFSM
from tg_bot.keyboards import place_manager_kb
from tg_bot.routers.role_model_fsm.manager_fsm import *
from tg_bot.routers.manager_ui.place_handlers.manager_get_place_handlers import (
    router as get_place_router,
)
from tg_bot.routers.manager_ui.place_handlers.manager_add_place_handlers import (
    router as add_place_router,
)
from tg_bot.routers.manager_ui.place_handlers.manager_delete_place_handlers import (
    router as delete_place_router,
)
from tg_bot.routers.manager_ui.place_handlers.manager_update_place_handlers import (
    router as update_place_router,
)
from tg_bot.utils_and_validators import drop_request

router = Router()


def init_manager_place_panel():
    router.include_router(get_place_router)
    router.include_router(add_place_router)
    router.include_router(delete_place_router)
    router.include_router(update_place_router)


@router.message(ManagerFSM.start_state, F.text == "Управление местами")
async def manage_places(message: Message, state: FSMContext):
    await state.set_state(ManagerFSM.place_state)
    await message.answer(
        "Вы вошли в режим управления местами.", reply_markup=place_manager_kb
    )


@router.message(Command("exit"), ManagerFSM.place_state)
@router.message(F.text == "Назад", ManagerFSM.place_state)
async def exit_handler(message: Message, state: FSMContext):
    await message.answer("Вы вышли из меню управления местами", reply_markup=manager_kb)
    await drop_request(state)
    await state.set_state(ManagerFSM.start_state)
