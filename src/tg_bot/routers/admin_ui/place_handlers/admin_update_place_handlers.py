from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import tg_bot.routers.manager_ui.place_handlers.update_place_functions as update_place_funcs
from tg_bot.routers.role_model_fsm.admin_fsm import AdminUpdatePlaceFSM
from tg_bot.tg_exceptions import PlaceNotFound
from tg_bot.keyboards import (
    place_manager_kb,
    UPDATE_DESCRIPTION_TAG,
    UPDATE_TAGS_TAG,
    SHOW_UPDATE_TAGS_TAG,
)
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector, KEYBOARD_PREFIX
from tg_bot.ui_components.TagSelector import TagSelector
from tg_bot.utils_and_validators import drop_request

router = Router()
geosuggest_selector = GeosuggestSelector(AdminUpdatePlaceFSM.select_place)
tag_selector = TagSelector(AdminUpdatePlaceFSM.enter_new_tags, router)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(
        AdminUpdatePlaceFSM.enter_place_name,
        AdminUpdatePlaceFSM.select_place,
        AdminUpdatePlaceFSM.enter_new_description,
        AdminUpdatePlaceFSM.press_update_buttons,
        AdminUpdatePlaceFSM.enter_new_tags,
    ),
)
async def exit_handler(message: Message, state: FSMContext):
    await drop_request(state)
    await message.answer(
        "Вы вышли из команды редактирования места", reply_markup=place_manager_kb
    )
    await state.set_state(AdminUpdatePlaceFSM.place_state)


@router.message(AdminUpdatePlaceFSM.place_state, F.text == "Редактировать место")
async def start_update_place_handler(message: Message, state: FSMContext):
    await update_place_funcs.start_update_function(message)
    await state.set_state(AdminUpdatePlaceFSM.enter_place_name)


@router.message(AdminUpdatePlaceFSM.enter_place_name, F.text)
async def enter_place_name_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    await update_place_funcs.show_geosuggest_menu(message, state, geosuggest_selector)
    await state.set_state(AdminUpdatePlaceFSM.select_place)


@router.callback_query(
    AdminUpdatePlaceFSM.select_place, F.data.contains(KEYBOARD_PREFIX)
)
async def selected_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        await update_place_funcs.selected_place(
            callback, state, session, geosuggest_selector, failure_kb=place_manager_kb
        )
        await state.set_state(AdminUpdatePlaceFSM.press_update_buttons)
    except PlaceNotFound:
        await state.set_state(AdminUpdatePlaceFSM.place_state)


@router.callback_query(
    AdminUpdatePlaceFSM.press_update_buttons, F.data == UPDATE_DESCRIPTION_TAG
)
async def start_description_enter_handler(callback: CallbackQuery, state: FSMContext):
    await update_place_funcs.start_description_enter_function(callback, state)
    await state.set_state(AdminUpdatePlaceFSM.enter_new_description)


@router.message(AdminUpdatePlaceFSM.enter_new_description, F.text)
async def enter_description_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    await update_place_funcs.enter_description_function(message, state, session)
    await state.set_state(AdminUpdatePlaceFSM.press_update_buttons)


@router.callback_query(
    AdminUpdatePlaceFSM.press_update_buttons, F.data == SHOW_UPDATE_TAGS_TAG
)
async def start_tag_selector_handler(callback: CallbackQuery, state: FSMContext):
    await update_place_funcs.start_tag_selector(callback, state, tag_selector)


@router.callback_query(AdminUpdatePlaceFSM.enter_new_tags, F.data == UPDATE_TAGS_TAG)
async def enter_new_tags_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await update_place_funcs.update_tags(callback, state, session)
    await state.set_state(AdminUpdatePlaceFSM.press_update_buttons)
