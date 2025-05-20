from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from tg_bot.keyboards import channel_kb
from tg_bot.routers.channel_fetch_router import (
    add_channel,
    get_channels,
    remove_channel,
)
from tg_bot.routers.manager_ui.manager import ManagerFSM
from tg_bot.routers.role_model_fsm.manager_fsm import *
from tg_bot.ui_components.Paginator import PaginatorService
from sqlalchemy.ext.asyncio import AsyncSession


def check_channel_tag(tag: str) -> bool:
    return (
        tag.startswith("@")
        and tag.isascii()
        and len(set(" ,.:/!\\\"'?") & set(tag)) == 0
    )


async def get_channels_for_paginator(
    page: int, place_per_page: int, session: AsyncSession
) -> list[str]:
    channels = await get_channels(session, page, place_per_page)
    return [
        f"Канал: @{channel["tag"]}\nДобавлен: @{channel["manager"]}"
        for channel in channels
    ]


POSTFIX = "channels"
CHANNELS_PER_PAGE = 5
channel_paginator_service = PaginatorService(
    POSTFIX,
    CHANNELS_PER_PAGE,
    get_channels_for_paginator,
    "Пока что к этом боту не привязан ни один телеграм канал",
)


async def show_channel_menu(message: Message, state: FSMContext, next_state: State):
    await state.set_state(next_state)
    await message.answer("Вы перешли в меню настроек каналов", reply_markup=channel_kb)


async def display_help(message: Message):
    await message.answer(
        """
Для того, чтобы добавить ТГ канал для его чтения:
1) Добавьте нашего бота, как администратора в канал/попросите админа канала добавить нашего
2) Нажмите кнопку "Добавить ТГ канал" и укажите ссылку на него (тег через @)
3) Бот добавлен

Удаление бота/запрещение на просмотр
1) Нажмите кнопку "Удалить канал"
2) Введите название ненужного канала
        """
    )


async def exit_channel_action(message: Message, state: FSMContext, next_state: State):
    await state.set_state(next_state)
    await message.answer(
        "Вы вышли. Никаких изменений не сделано.", reply_markup=channel_kb
    )


async def add_channel_button(message: Message, state: FSMContext, next_state: State):
    await message.answer(
        "Введите название канала и убедитесь, что бот добавлен в канал!\nИли введите /exit для выхода",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(next_state)


async def add_channel_action(
    message: Message, state: FSMContext, next_state: State, session: AsyncSession
):
    if not check_channel_tag(message.text):
        await message.answer("Неверный формат канала. Для выхода пропишите /exit.")
        return
    if await add_channel(message.text[1:], message.from_user.id, session):
        await state.set_state(next_state)
        await message.answer("Канал успешно добавлен", reply_markup=channel_kb)
        return
    await message.answer(
        "Данный канал уже добавлен другим пользователем, попробуйте другой или напишите /exit для выхода!"
    )


async def remove_action_button(message: Message, state: FSMContext, next_state: State):
    await state.set_state(next_state)
    await message.answer(
        "Напишите через @ название канала для удаления. Для выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )


async def remove_channel_action(
    message: Message, state: FSMContext, next_state: State, session: AsyncSession
):
    if not check_channel_tag(message.text):
        await message.answer("Неправильный формат. Для выхода напишите /exit.")
        return
    if await remove_channel(message.text[1:], session):
        await state.set_state(next_state)
        await message.answer(
            f"Канал {message.text} был удалён", reply_markup=channel_kb
        )
        return
    await message.answer(
        f"Канал {message.text} не найден. Попробуйте ещё раз или выйдите, написав /exit"
    )
