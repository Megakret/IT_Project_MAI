from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession
import tg_bot.routers.manager_ui.place_handlers.delete_place_functions as delete_place_funcs
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerDeletePlaceFSM
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector, KEYBOARD_PREFIX
from tg_bot.keyboards import back_kb, place_manager_kb

router = Router()

geosuggest_selector = GeosuggestSelector(ManagerDeletePlaceFSM.select_place)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(ManagerDeletePlaceFSM.enter_place_name, ManagerDeletePlaceFSM.select_place),
)
async def exit_handler(message: Message, state: FSMContext):
    await message.answer(
        "Вы вышли из команды удаления места", reply_markup=place_manager_kb
    )
    await state.set_state(ManagerDeletePlaceFSM.place_state)


@router.message(F.text == "Удалить место", ManagerDeletePlaceFSM.place_state)
async def start_handler(message: Message, state: FSMContext):
    await delete_place_funcs.start_delete_place_function(message)
    await state.set_state(ManagerDeletePlaceFSM.enter_place_name)


@router.message(ManagerDeletePlaceFSM.enter_place_name, F.text)
async def show_menu_handler(message: Message, state: FSMContext):
    await delete_place_funcs.show_geosuggest_menu(message, state, geosuggest_selector)


@router.callback_query(ManagerDeletePlaceFSM.select_place, F.data.contains(KEYBOARD_PREFIX))
async def delete_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        await delete_place_funcs.delete_place_function(
            callback, state, session, geosuggest_selector, place_manager_kb
        )
        await state.set_state(ManagerDeletePlaceFSM.place_state)
    except PlaceNotFound:
        await state.set_state(ManagerDeletePlaceFSM.place_state)
