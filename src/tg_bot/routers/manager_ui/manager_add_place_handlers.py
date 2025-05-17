import tg_bot.routers.manager_ui.manager_add_place_functions as add_place_funcs
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerAddPlaceFSM, ManagerFSM
from tg_bot.ui_components.GeosuggestSelector import KEYBOARD_PREFIX, GeosuggestSelector
from tg_bot.ui_components.TagSelector import (
    SelectTagsStates,
)
from tg_bot.keyboards import (
    INSERT_PLACE_TAGS_TAG,
)

router = Router()
geosuggest_selector = GeosuggestSelector(ManagerAddPlaceFSM.choose_place)


@router.message(F.text == "Управление местами", ManagerFSM.start_state)
async def enter_place_state_handler(message: Message, state: FSMContext):
    await add_place_funcs.enter_place_state(message)
    await state.set_state(ManagerAddPlaceFSM.start_state)


@router.message(F.text == "Добавить место", ManagerAddPlaceFSM.start_state)
@router.message(Command("add_place"), ManagerAddPlaceFSM.start_state)
async def add_place_handler(message: Message, state: FSMContext) -> None:
    await add_place_funcs.add_place_handler(message, state)
    await state.set_state(ManagerAddPlaceFSM.enter_place)


@router.message(ManagerAddPlaceFSM.enter_place)
async def show_suggestions(message: Message, state: FSMContext):
    await add_place_funcs.show_suggestions(message, state, geosuggest_selector)


@router.callback_query(
    F.data.contains(KEYBOARD_PREFIX), ManagerAddPlaceFSM.choose_place
)
async def choose_suggested_place(callback: CallbackQuery, state: FSMContext):
    print("chose place")
    await add_place_funcs.choose_suggested_place(callback, state, geosuggest_selector)
    await state.set_state(ManagerAddPlaceFSM.enter_description)


@router.message(ManagerAddPlaceFSM.enter_description)
async def get_description(message: Message, state: FSMContext):
    await add_place_funcs.get_description(message, state)
    await state.set_state(SelectTagsStates.selecting_tag)


@router.callback_query(F.data == INSERT_PLACE_TAGS_TAG, SelectTagsStates.selecting_tag)
async def insert_tags(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await add_place_funcs.insert_tags(callback, state, session)
    await state.set_state(ManagerAddPlaceFSM.start_state)
