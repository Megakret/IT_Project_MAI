from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import tg_bot.routers.manager_ui.place_handlers.update_place_functions as update_place_funcs
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerUpdatePlaceFSM
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import back_kb, place_manager_kb

router = Router()


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(
        ManagerUpdatePlaceFSM.enter_place_id,
        ManagerUpdatePlaceFSM.enter_new_name,
        ManagerUpdatePlaceFSM.enter_new_description,
    ),
)
async def exit_handler(message: Message, state: FSMContext):
    await message.answer("Вы вышли из команды редактирования места", reply_markup=place_manager_kb)
    await state.set_state(ManagerUpdatePlaceFSM.place_state)


@router.message(ManagerUpdatePlaceFSM.place_state, F.text == "Редактировать место")
async def start_update_place_handler(message: Message, state: FSMContext):
    await update_place_funcs.start_update_function(message)
    await state.set_state(ManagerUpdatePlaceFSM.enter_place_id)


@router.message(ManagerUpdatePlaceFSM.enter_place_id, F.text)
async def enter_place_id_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    try:
        await update_place_funcs.enter_id_function(message, state, session)
        await state.set_state(ManagerUpdatePlaceFSM.enter_new_name)
    except PlaceNotFound:
        await state.set_state(ManagerUpdatePlaceFSM.place_state)
    except ValueError:
        pass


@router.message(ManagerUpdatePlaceFSM.enter_new_name, F.text)
async def enter_name_handler(message: Message, state: FSMContext):
    await update_place_funcs.enter_name_function(message, state)
    await state.set_state(ManagerUpdatePlaceFSM.enter_new_description)


@router.message(ManagerUpdatePlaceFSM.enter_new_description, F.text)
async def enter_description_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    await update_place_funcs.enter_description_function(message, state, session, place_manager_kb)
    await state.set_state(ManagerUpdatePlaceFSM.place_state)
