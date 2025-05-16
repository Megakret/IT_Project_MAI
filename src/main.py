import dotenv
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, Router
from database.db_functions import init_database
from tg_bot.middlewares.DatabaseConnectionMiddleware import DatabaseConnectionMiddleware
from tg_bot.routers.channel_fetch_router import router as channel_router
from tg_bot.routers.manager_ui.manager import router as manager_router
from tg_bot.routers.manager_ui.manager_channel import router as manager_router_channel
from tg_bot.routers.manager_ui.manager_place import router as manager_router_place
from tg_bot.routers.command_router import router as command_router
from tg_bot.routers.start_handler import router as start_router
from tg_bot.routers.main_user_router import router as main_user_router
from tg_bot.routers.main_user_router import initialize_user_routers
from tg_bot.routers.manager_ui.manager_place import init_manager_place_panel


async def main() -> None:
    bot = Bot(getenv("BOT_TOKEN").replace(r"\x3a", ":"))
    session_maker = init_database()
    dp = Dispatcher()
    dp.update.middleware(DatabaseConnectionMiddleware(session_maker))
    dp.include_router(start_router)
    dp.include_router(channel_router)
    dp.include_router(manager_router)
    dp.include_router(manager_router_channel)
    init_manager_place_panel()
    dp.include_router(manager_router_place)
    initialize_user_routers(session_maker)
    dp.include_router(main_user_router)
    dp.include_router(command_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been turned off")
