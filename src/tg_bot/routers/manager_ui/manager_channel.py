from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from tg_bot.keyboards import channel_kb
from tg_bot.routers.channel_fetch_router import (
    add_channel,
    get_channels,
    remove_channel,
)
from tg_bot.routers.manager_ui.manager import ManagerFSM
from tg_bot.routers.role_model_fsm.admin_fsm import *
from tg_bot.routers.role_model_fsm.manager_fsm import *

router = Router()


def check_channel_tag(tag: str) -> bool:
    return (
        tag.startswith("@")
        and tag.isascii()
        and len(set(" ,.:/!\\\"'?") & set(tag)) == 0
    )


@router.message(F.text == "Управлене ТГ каналами", AdminFSM.start_state)
@router.message(F.text == "Управление ТГ каналами", ManagerFSM.start_state)
async def show_channel_menu(message: Message, state: FSMContext):
    await state.set_state(ManagerFSM.channel_state)
    await message.answer("Вы перешли в меню настроек каналов", reply_markup=channel_kb)


@router.message(F.text == "Помощь", ManagerFSM.channel_state)
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


@router.message(Command("exit"), ChannelFSM.add_channel_state)
@router.message(Command("exit"), ChannelFSM.remove_channel_state)
async def exit_channel_action(message: Message, state: FSMContext):
    await state.set_state(ManagerFSM.channel_state)
    await message.answer(
        "Вы вышли. Никаких изменений не сделано.", reply_markup=channel_kb
    )


@router.message(F.text == "Добавить ТГ канал", ManagerFSM.channel_state)
async def add_channel_button(message: Message, state: FSMContext):
    await message.answer(
        "Введите название канала и убедитесь, что бот добавлен в канал!\nИли введите /exit для выхода",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ChannelFSM.add_channel_state)


@router.message(ChannelFSM.add_channel_state)
async def add_channel_action(message: Message, state: FSMContext):
    if not check_channel_tag(message.text):
        await message.answer("Неверный формат канала. Для выхода пропишите /exit.")
        return
    if add_channel(message.text, f"@{message.from_user.username}"):
        await state.set_state(ManagerFSM.channel_state)
        await message.answer("Канал успешно добавлен", reply_markup=channel_kb)
        return
    await message.answer(
        "Данный канал уже добавлен другим пользователем, попробуйте другой или напишите /exit для выхода!"
    )


@router.message(F.text == "Подключённые каналы", ManagerFSM.channel_state)
async def display_connected_channels(message: Message):
    channels = get_channels()
    await message.answer(
        "\n------------\n".join(
            f"Канал: {channel["tag"]}\nДобавлен: {channel["manager"]}"
            for channel in channels
        )
        if len(channels) > 0
        else "Каналов нет"
    )


@router.message(F.text == "Удалить канал", ManagerFSM.channel_state)
async def remove_action_button(message: Message, state: FSMContext):
    await state.set_state(ChannelFSM.remove_channel_state)
    await message.answer(
        "Напишите через @ название канала для удаления. Для выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(ChannelFSM.remove_channel_state)
async def remove_channel_action(message: Message, state: FSMContext):
    if not check_channel_tag(message.text):
        await message.answer("Неправильный формат. Для выхода напишите /exit.")
        return
    if remove_channel(message.text):
        await state.set_state(ManagerFSM.channel_state)
        await message.answer(
            f"Канал {message.text} был удалён", reply_markup=channel_kb
        )
        return
    await message.answer(
        f"Канал {message.text} не найден. Попробуйте ещё раз или выйдите, написав /exit"
    )
