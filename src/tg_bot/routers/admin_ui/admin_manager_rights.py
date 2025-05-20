from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, AdminChannelFSM
from tg_bot.routers.manager_ui.manager_functions import *
from tg_bot.keyboards import NEXT_PAGE, PREV_PAGE, INDICATOR_CLICKED

router = Router()


@router.message(F.text == "Управление ТГ каналами", AdminFSM.start_state)
async def show_channel_menu_manager(message: Message, state: FSMContext):
    await show_channel_menu(message, state, AdminFSM.channel_state)


@router.message(F.text == "Помощь", AdminFSM.channel_state)
async def display_help_manager(message: Message):
    await display_help(message)


@router.message(Command("exit"), AdminChannelFSM.add_channel_state)
@router.message(Command("exit"), AdminChannelFSM.remove_channel_state)
async def exit_channel_action_manager(message: Message, state: FSMContext):
    print("Hello")
    await exit_channel_action(message, state, AdminFSM.channel_state)


@router.message(F.text == "Добавить ТГ канал", AdminFSM.channel_state)
async def add_channel_button_manager(message: Message, state: FSMContext):
    await add_channel_button(message, state, AdminChannelFSM.add_channel_state)


@router.message(AdminChannelFSM.add_channel_state)
async def add_channel_action_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    print("dasfasdfdasf")
    await add_channel_action(message, state, AdminFSM.channel_state, session)


@router.message(F.text == "Подключённые каналы", AdminFSM.channel_state)
async def display_connected_channels_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    await channel_paginator_service.start_paginator(message, state, session)


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


@router.message(F.text == "Удалить канал", AdminFSM.channel_state)
async def remove_action_button_manager(message: Message, state: FSMContext):
    await remove_action_button(message, state, AdminChannelFSM.remove_channel_state)


@router.message(AdminChannelFSM.remove_channel_state)
async def remove_channel_action_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    await remove_channel_action(message, state, AdminFSM.channel_state, session)
