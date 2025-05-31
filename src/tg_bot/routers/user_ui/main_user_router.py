from aiogram import Router, F
from aiogram.types import Message, ErrorEvent
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from tg_bot.keyboards import get_user_keyboard
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tg_bot.routers.user_ui.get_places_by_tag_handler import (
    router as get_places_by_tag_router,
)
from tg_bot.routers.user_ui.add_place_handler import router as add_place_router
from tg_bot.routers.user_ui.place_list_handlers import router as place_list_router
from tg_bot.routers.user_ui.user_place_list_handler import (
    router as user_place_list_router,
)
from tg_bot.routers.user_ui.get_place_info_handler import (
    router as get_place_info_router,
)
from tg_bot.routers.user_ui.get_user_comments_handler import (
    router as get_user_comments_router,
)
from tg_bot.routers.user_ui.command_router import router as command_router
from tg_bot.routers.user_ui.user_fsm import UserFSM
from tg_bot.middlewares.UserExistenceCheckMiddleware import UserExistenceCheckMiddleware
from tg_bot.utils_and_validators import drop_request

import logging
from tg_bot.loggers.user_logger import user_log_handler

router = Router()
logger = logging.getLogger(__name__)
logger.addHandler(user_log_handler)


def initialize_user_routers(session_maker: async_sessionmaker):
    router.include_router(add_place_router)
    router.include_router(place_list_router)
    router.include_router(user_place_list_router)
    router.include_router(get_place_info_router)
    router.include_router(get_places_by_tag_router)
    router.include_router(get_user_comments_router)
    router.include_router(command_router)
    router.message.middleware(UserExistenceCheckMiddleware(session_maker))
    router.callback_query.middleware(UserExistenceCheckMiddleware(session_maker))


@router.message(Command("exit"))
@router.message(F.text == "Назад")
async def exit_command(message: Message, state: FSMContext, session: AsyncSession):
    current_state: State = await state.get_state()
    await drop_request(state)
    if current_state is UserFSM.start_state:
        await message.answer("Вы итак в главном меню")
    else:
        await message.answer(
            "Вы вышли в главное меню",
            reply_markup=(await get_user_keyboard(session, message.from_user.id)),
        )
        await state.set_state(UserFSM.start_state)


@router.error()
async def handle_errors(error: ErrorEvent):
    logger.critical("Uncaught error appeared: %s", error.exception, exc_info=True)
