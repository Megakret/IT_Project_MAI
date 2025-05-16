from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, ChannelFSM
from tg_bot.routers.manager_ui.manager_functions import *

router = Router()


@router.message(F.text == "Управление ТГ каналами", AdminFSM.start_state)
async def show_channel_menu_manager(message: Message, state: FSMContext):
    await show_channel_menu(message, state, AdminFSM.channel_state)


@router.message(F.text == "Помощь", AdminFSM.channel_state)
async def display_help_manager(message: Message):
    await display_help(message)


@router.message(Command("exit"), ChannelFSM.add_channel_state)
@router.message(Command("exit"), ChannelFSM.remove_channel_state)
async def exit_channel_action_manager(message: Message, state: FSMContext):
    await exit_channel_action(message, state)


@router.message(F.text == "Добавить ТГ канал", AdminFSM.channel_state)
async def add_channel_button_manager(message: Message, state: FSMContext):
    await add_channel_button(message, state, ChannelFSM.add_channel_state)


@router.message(ChannelFSM.add_channel_state)
async def add_channel_action_manager(message: Message, state: FSMContext):
    await add_channel_action(message, state, AdminFSM.channel_state)


@router.message(F.text == "Подключённые каналы", AdminFSM.channel_state)
async def display_connected_channels_manager(message: Message):
    await display_connected_channels(message)


@router.message(F.text == "Удалить канал", AdminFSM.channel_state)
async def remove_action_button_manager(message: Message, state: FSMContext):
    await remove_action_button(message, state, ChannelFSM.remove_channel_state)


@router.message(ChannelFSM.remove_channel_state)
async def remove_channel_action_manager(message: Message, state: FSMContext):
    await remove_channel_action(message, state, AdminFSM.channel_state)
