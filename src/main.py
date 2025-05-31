import asyncio
from os import getenv
from aiogram import Bot, Dispatcher
import logging
from tg_bot.loggers.start_shutdown_logger import (
    start_shutdown_log_handler,
    init_start_shutdown_logger,
)
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH

from database.db_functions import init_database

from tg_bot.DispatcherHandler import DispatcherHandler
from tg_bot.middlewares.DatabaseConnectionMiddleware import DatabaseConnectionMiddleware
from tg_bot.routers.start_handler import router as start_router
from tg_bot.routers.admin_ui.admin import router as admin_router
from tg_bot.routers.admin_ui.admin import init_admin_routers
from tg_channel_fetcher.channel_fetch_router import router as channel_fetch_router
from tg_bot.routers.user_ui.main_user_router import router as main_user_router
from tg_bot.routers.user_ui.main_user_router import initialize_user_routers
from tg_bot.routers.manager_ui.manager import router as manager_router
from tg_bot.routers.manager_ui.manager import init_manager_router

from tg_bot.loggers.user_logger import init_user_logger
from tg_bot.loggers.admin_logger import init_admin_logger
from tg_bot.loggers.manager_logger import init_manager_logger
from tg_bot.loggers.channel_fetch_logger import init_channel_logger


async def main() -> None:
    bot = Bot(getenv("BOT_TOKEN").replace(r"\x3a", ":"))
    session_maker = init_database()
    dp = Dispatcher()
    DispatcherHandler.set_data(bot, dp)
    dp.update.middleware(DatabaseConnectionMiddleware(session_maker))
    dp.include_router(channel_fetch_router)
    init_admin_routers()
    dp.include_router(admin_router)
    dp.include_router(start_router)
    init_manager_router()
    dp.include_router(manager_router)
    initialize_user_routers(session_maker)
    dp.include_router(main_user_router)
    init_user_logger()
    init_admin_logger()
    init_manager_logger()
    init_channel_logger()
    await dp.start_polling(bot)


if __name__ == "__main__":
    init_start_shutdown_logger()
    start_logger = logging.getLogger(__name__)
    start_logger.addHandler(start_shutdown_log_handler)
    try:
        start_logger.critical("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        start_logger.critical("Bot has been turned off")
