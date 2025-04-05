from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from tg_bot.aiogram_coros import custom_clear
from tg_bot.test_utils.place_list.place_list_placeholder import (
    get_places_by_page,
    get_page_count,
)
from tg_bot.keyboards import generate_page_kb

router = Router()


def get_formatted_list(page: int) -> str:
    place_list: list[str] = get_places_by_page(page)
    text: str = "\n-----------\n".join(place_list)
    return text


async def show_page(message: Message, current_page: int) -> bool:
    max_page: int = get_page_count()
    text: str = get_formatted_list(current_page)
    await message.edit_text(text=text)
    await message.edit_reply_markup(
        reply_markup=generate_page_kb(current_page, max_page)
    )


@router.message(Command("place_list"))
async def show_place_list(message: Message, state: FSMContext):
    print("it works")
    max_page: int = get_page_count()
    text: str = get_formatted_list(0)
    await custom_clear(state)
    await state.update_data(page=0)
    await message.answer(text=text, reply_markup=generate_page_kb(0, max_page))


@router.callback_query(F.data == "next_page")
async def show_next_page(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 0)
    try:
        await show_page(callback.message, current_page + 1)
        await state.update_data(page=current_page + 1)
    except KeyError:
        await callback.answer("Вы на последней странице")


@router.callback_query(F.data == "prev_page")
async def show_next_page(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 0)
    try:
        await show_page(callback.message, current_page - 1)
        await state.update_data(page=current_page - 1)
    except KeyError:
        await callback.answer("Вы на первой странице")


@router.callback_query(F.data == "page_indicator")
async def indicator_clicked(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    current_page: int = data.get("page", 0)
    await callback.answer(f"Вы на странице {current_page + 1}")
