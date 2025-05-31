import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, Router
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been turned off")
