import tg_bot.routers.manager_ui.place_handlers.manager_add_place_functions as add_place_funcs
from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerAddPlaceFSM
from tg_bot.ui_components.GeosuggestSelector import KEYBOARD_PREFIX, GeosuggestSelector
from tg_bot.ui_components.TagSelector import TagSelector
from tg_bot.keyboards import INSERT_PLACE_TAGS_TAG, place_manager_kb
from tg_bot.keyboards import place_manager_kb
from tg_bot.tg_exceptions import MessageIsTooLarge
from tg_bot.utils_and_validators import drop_request

router = Router()
geosuggest_selector = GeosuggestSelector(ManagerAddPlaceFSM.choose_place)
tag_selector = TagSelector(
    selecting_state=ManagerAddPlaceFSM.selecting_tags, router=router
)


@router.message(
    or_f(Command("exit"), F.text == "Назад"),
    or_f(
        ManagerAddPlaceFSM.enter_place,
        ManagerAddPlaceFSM.choose_place,
        ManagerAddPlaceFSM.enter_description,
        ManagerAddPlaceFSM.selecting_tags,
    ),
)
async def exit_handler(message: Message, state: FSMContext):
    await drop_request(state)
    await message.answer(
        "Вы вышли из команды удаления места", reply_markup=place_manager_kb
    )
    await state.set_state(ManagerAddPlaceFSM.place_state)


@router.message(F.text == "Добавить место", ManagerAddPlaceFSM.place_state)
@router.message(Command("add_place"), ManagerAddPlaceFSM.place_state)
async def add_place_handler(message: Message, state: FSMContext) -> None:
    await add_place_funcs.add_place_handler(message, state)
    await state.set_state(ManagerAddPlaceFSM.enter_place)


@router.message(ManagerAddPlaceFSM.enter_place)
async def show_suggestions(message: Message, state: FSMContext):
    await add_place_funcs.show_suggestions(message, state, geosuggest_selector)


@router.callback_query(
    F.data.contains(KEYBOARD_PREFIX), ManagerAddPlaceFSM.choose_place
)
async def choose_suggested_place(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        await add_place_funcs.choose_suggested_place(
            callback, state, geosuggest_selector, session
        )
        await state.set_state(ManagerAddPlaceFSM.enter_description)
    except ValueError as e:
        print(e)
        await callback.message.answer(
            "Это место уже было добавлено.", reply_markup=place_manager_kb
        )
        await state.set_state(ManagerAddPlaceFSM.place_state)


@router.message(ManagerAddPlaceFSM.enter_description)
async def get_description(message: Message, state: FSMContext):
    await add_place_funcs.get_description(message, state, tag_selector)


@router.callback_query(
    F.data == INSERT_PLACE_TAGS_TAG, ManagerAddPlaceFSM.selecting_tags
)
async def insert_tags(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await add_place_funcs.insert_tags(callback, state, session, place_manager_kb)
    await state.set_state(ManagerAddPlaceFSM.place_state)
