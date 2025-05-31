from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession
import tg_bot.routers.manager_ui.place_handlers.delete_place_functions as delete_place_funcs
from tg_bot.routers.role_model_fsm.admin_fsm import AdminDeletePlaceFSM
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector, KEYBOARD_PREFIX
from tg_bot.keyboards import place_manager_kb
import logging
from tg_bot.loggers.admin_logger import admin_log_handler

router = Router()

geosuggest_selector = GeosuggestSelector(AdminDeletePlaceFSM.select_place)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(AdminDeletePlaceFSM.enter_place_name, AdminDeletePlaceFSM.select_place),
)
async def exit_handler(message: Message, state: FSMContext):
    await message.answer(
        "Вы вышли из команды удаления места", reply_markup=place_manager_kb
    )
    await state.set_state(AdminDeletePlaceFSM.place_state)


@router.message(F.text == "Удалить место", AdminDeletePlaceFSM.place_state)
async def start_handler(message: Message, state: FSMContext):
    await delete_place_funcs.start_delete_place_function(message)
    await state.set_state(AdminDeletePlaceFSM.enter_place_name)


@router.message(AdminDeletePlaceFSM.enter_place_name, F.text)
async def show_menu_handler(message: Message, state: FSMContext):
    await delete_place_funcs.show_geosuggest_menu(message, state, geosuggest_selector)


@router.callback_query(
    AdminDeletePlaceFSM.select_place, F.data.contains(KEYBOARD_PREFIX)
)
async def delete_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        await delete_place_funcs.delete_place_function(
            callback, state, session, geosuggest_selector, place_manager_kb
        )
        await state.set_state(AdminDeletePlaceFSM.place_state)
    except PlaceNotFound:
        await state.set_state(AdminDeletePlaceFSM.place_state)
