from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.aiogram_coros import custom_clear
from tg_bot.keyboards import generate_page_kb, starter_kb
from database.db_functions import get_places, Place

router = Router()
PLACES_PER_PAGE = 5

class NoMorePlacesException(Exception):
    pass

async def get_formatted_list(session: AsyncSession, page: int, places_per_page: int) -> str:
    place_list: list[Place] = await get_places(session, page, places_per_page)
    place_formatted_list: map[str] = map(lambda x: f"{x.name}\n{x.address}\n{x.desc}", place_list)
    text: str = "\n-----------\n".join(place_formatted_list)
    return text


async def show_page(session: AsyncSession, message: Message, current_page: int) -> bool:
    text: str = await get_formatted_list(session, current_page, PLACES_PER_PAGE)
    if(text == ""):
        raise NoMorePlacesException()
    await message.edit_text(text=text)
    await message.edit_reply_markup(
        reply_markup=generate_page_kb(current_page)
    )


@router.message(Command("place_list"))
async def show_place_list(message: Message, state: FSMContext, session: AsyncSession):
    # print("it works")
    text: str = await get_formatted_list(session, 1, 5)
    await custom_clear(state)
    await state.update_data(page=1)
    await message.answer(text=text, reply_markup=generate_page_kb(1))


@router.callback_query(F.data == "next_page")
async def show_next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 1)
    try:
        await show_page(session, callback.message, current_page + 1)
        await state.update_data(page=current_page + 1)
    except NoMorePlacesException:
        await callback.answer("Вы на последней странице")


@router.callback_query(F.data == "prev_page")
async def show_next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 1)
    try:
        if(current_page == 1):
            raise NoMorePlacesException()
        await show_page(session, callback.message, current_page - 1)
        await state.update_data(page=current_page - 1)
    except NoMorePlacesException: # to ensure that if we delete some places from db, user wont get stuck
        await show_page(session, callback.message, 1)
        await state.update_data(page=1)
        await callback.answer("Вы на первой странице")


@router.callback_query(F.data == "page_indicator")
async def indicator_clicked(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 1)
    await callback.answer(f"Вы на странице {current_page}")
