from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
)
import tg_bot.routers.manager_ui.place_handlers.get_place_functions as get_place_funcs
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerGetPlaceFSM
from tg_bot.keyboards import place_manager_kb
from tg_bot.utils_and_validators import drop_request

router = Router()
geosuggest_selector = GeosuggestSelector(ManagerGetPlaceFSM.choose_place)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(ManagerGetPlaceFSM.enter_place, ManagerGetPlaceFSM.choose_place),
)
async def exit_handler(message: Message, state: FSMContext):
    await drop_request(state)
    await message.answer(
        "Вы вышли из команды поиска места", reply_markup=place_manager_kb
    )
    await state.set_state(ManagerGetPlaceFSM.place_state)


@router.message(F.text == "Найти место", ManagerGetPlaceFSM.place_state)
async def start_handler(message: Message, state: FSMContext):
    await get_place_funcs.start_get_place_function(message)
    await state.set_state(ManagerGetPlaceFSM.enter_place)


@router.message(ManagerGetPlaceFSM.enter_place, F.text)
async def start_geosuggest_handler(message: Message, state: FSMContext):
    await get_place_funcs.enter_place_function(message, state, geosuggest_selector)


@router.callback_query(
    ManagerGetPlaceFSM.choose_place, F.data.contains(KEYBOARD_PREFIX)
)
async def output_found_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await get_place_funcs.place_selected_function(
        callback, state, session, geosuggest_selector, place_manager_kb
    )
    await state.set_state(ManagerGetPlaceFSM.place_state)
