import dotenv
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, Router
from database.db_functions import init_database
from tg_bot.middlewares.DatabaseConnectionMiddleware import DatabaseConnectionMiddleware
from tg_bot.routers.add_place_handler import router as add_place_router
from tg_bot.routers.place_list_handlers import router as place_list_router
from tg_bot.routers.user_place_list_handler import router as user_place_list_router


async def main() -> None:
    dotenv.load_dotenv()
    bot = Bot(getenv("BOT_TOKEN"))
    session_maker = init_database()
    dp = Dispatcher()
    dp.update.middleware(DatabaseConnectionMiddleware(session_maker))
    dp.include_router(add_place_router)
    dp.include_router(place_list_router)
    dp.include_router(user_place_list_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been turned off")
