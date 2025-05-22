from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.keyboards import channel_kb, NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED
from tg_bot.routers.manager_ui.manager import ManagerFSM
from tg_bot.routers.role_model_fsm.manager_fsm import *
from tg_bot.routers.manager_ui.manager_functions import *

router = Router()


@router.message(F.text == "Управление ТГ каналами", ManagerFSM.start_state)
async def show_channel_menu_manager(message: Message, state: FSMContext):
    await show_channel_menu(message, state, ManagerFSM.channel_state)


@router.message(F.text == "Помощь", ManagerFSM.channel_state)
async def display_help_manager(message: Message):
    await display_help(message)


@router.message(Command("exit"), ManagerChannelFSM.add_channel_state)
@router.message(Command("exit"), ManagerChannelFSM.remove_channel_state)
async def exit_channel_action_manager(message: Message, state: FSMContext):
    await exit_channel_action(message, state)


@router.message(F.text == "Добавить ТГ канал", ManagerFSM.channel_state)
async def add_channel_button_manager(message: Message, state: FSMContext):
    await add_channel_button(message, state, ManagerChannelFSM.add_channel_state)


@router.message(ManagerChannelFSM.add_channel_state)
async def add_channel_action_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    await add_channel_action(message, state, ManagerFSM.channel_state, session)


@router.message(F.text == "Подключённые каналы", ManagerFSM.channel_state)
async def display_connected_channels_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    await channel_paginator_service.start_paginator(message, state, session)


@router.message(F.text == "Удалить канал", ManagerFSM.channel_state)
async def remove_action_button_manager(message: Message, state: FSMContext):
    await remove_action_button(message, state, ManagerChannelFSM.remove_channel_state)


@router.message(ManagerChannelFSM.remove_channel_state)
async def remove_channel_action_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    await remove_channel_action(message, state, ManagerFSM.channel_state, session)


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, ManagerFSM.channel_state)
async def next_page_channel_action(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await channel_paginator_service.show_next_page(callback, state, session)


@router.callback_query(F.data == PREV_PAGE + POSTFIX, ManagerFSM.channel_state)
async def prev_page_channel_action(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await channel_paginator_service.show_prev_page(callback, state, session)


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX, ManagerFSM.channel_state)
async def indicator_clicked(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await channel_paginator_service.indicator_clicked(callback, state, session)
