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
from tg_bot.routers.role_model_fsm.manager_fsm import *

router = Router()
