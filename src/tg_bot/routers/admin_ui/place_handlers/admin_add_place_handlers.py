import tg_bot.routers.manager_ui.place_handlers.manager_add_place_functions as add_place_funcs
from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.routers.role_model_fsm.admin_fsm import AdminAddPlaceFSM
from tg_bot.ui_components.GeosuggestSelector import KEYBOARD_PREFIX, GeosuggestSelector
from tg_bot.ui_components.TagSelector import TagSelector
from tg_bot.keyboards import INSERT_PLACE_TAGS_TAG, place_manager_kb
from tg_bot.keyboards import place_manager_kb
from tg_bot.tg_exceptions import MessageIsTooLarge
import logging
from tg_bot.loggers.admin_logger import admin_log_handler

logger = logging.getLogger(__name__)
logger.addHandler(admin_log_handler)
router = Router()
geosuggest_selector = GeosuggestSelector(AdminAddPlaceFSM.choose_place)
tag_selector = TagSelector(
    selecting_state=AdminAddPlaceFSM.selecting_tags, router=router
)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(
        AdminAddPlaceFSM.enter_place,
        AdminAddPlaceFSM.choose_place,
        AdminAddPlaceFSM.enter_description,
        AdminAddPlaceFSM.selecting_tags,
    ),
)
async def exit_handler(message: Message, state: FSMContext):
    await message.answer(
        "Вы вышли из команды удаления места", reply_markup=place_manager_kb
    )
    await state.set_state(AdminAddPlaceFSM.place_state)


@router.message(F.text == "Добавить место", AdminAddPlaceFSM.place_state)
@router.message(Command("add_place"), AdminAddPlaceFSM.place_state)
async def add_place_handler(message: Message, state: FSMContext) -> None:
    await add_place_funcs.add_place_handler(message, state)
    await state.set_state(AdminAddPlaceFSM.enter_place)


@router.message(AdminAddPlaceFSM.enter_place)
async def show_suggestions(message: Message, state: FSMContext):
    await add_place_funcs.show_suggestions(message, state, geosuggest_selector)


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), AdminAddPlaceFSM.choose_place)
async def choose_suggested_place(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        await add_place_funcs.choose_suggested_place(
            callback, state, geosuggest_selector, session
        )
        await state.set_state(AdminAddPlaceFSM.enter_description)
    except ValueError as e:
        logger.warning(e)
        await callback.message.answer(
            "Это место уже было добавлено.", reply_markup=place_manager_kb
        )
        await state.set_state(AdminAddPlaceFSM.place_state)


@router.message(AdminAddPlaceFSM.enter_description)
async def get_description(message: Message, state: FSMContext):
    await add_place_funcs.get_description(message, state, tag_selector)


@router.callback_query(F.data == INSERT_PLACE_TAGS_TAG, AdminAddPlaceFSM.selecting_tags)
async def insert_tags(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await add_place_funcs.insert_tags(callback, state, session, place_manager_kb)
    await state.set_state(AdminAddPlaceFSM.place_state)
