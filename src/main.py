import dotenv
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, Router
from sqlalchemy.ext.asyncio import async_sessionmaker
from database.db_functions import init_database
from tg_bot.middlewares.DatabaseConnectionMiddleware import DatabaseConnectionMiddleware
from tg_bot.middlewares.UserExistenceCheckMiddleware import UserExistenceCheckMiddleware
from tg_bot.routers.add_place_handler import router as add_place_router
from tg_bot.routers.place_list_handlers import router as place_list_router
from tg_bot.routers.user_place_list_handler import router as user_place_list_router
from tg_bot.routers.get_place_info_handler import router as get_place_info_router
from tg_bot.routers.gpt_talk_handlers import router as gpt_router
from tg_bot.routers.channel_fetch_router import router as channel_router
from tg_bot.routers.manager_ui.manager import router as manager_router
from tg_bot.routers.manager_ui.manager_channel import router as manager_router_channel
from tg_bot.routers.get_places_by_tag_handler import router as get_places_by_tag_router
from tg_bot.routers.command_router import router as command_router
from tg_bot.routers.start_handler import router as start_router
from tg_bot.ui_components.TagSelector import generate_tag_handlers


async def main() -> None:
    bot = Bot(getenv("BOT_TOKEN").replace(r"\x3a", ":"))
    session_maker = init_database()
    dp = Dispatcher()
    user_commands_router = Router()
    dp.update.middleware(DatabaseConnectionMiddleware(session_maker))
    attach_user_command_routers(user_commands_router, session_maker)
    dp.include_router(start_router)
    dp.include_router(user_commands_router)
    dp.include_router(manager_router)
    dp.include_router(manager_router_channel)
    await dp.start_polling(bot)


def attach_user_command_routers(router: Router, session_maker: async_sessionmaker):
    router.include_router(add_place_router)
    router.include_router(place_list_router)
    router.include_router(user_place_list_router)
    router.include_router(get_place_info_router)
    router.include_router(gpt_router)
    router.include_router(channel_router)
    router.include_router(get_places_by_tag_router)
    router.include_router(command_router)
    generate_tag_handlers(get_places_by_tag_router)
    generate_tag_handlers(add_place_router)
    router.message.middleware(UserExistenceCheckMiddleware(session_maker))
    router.callback_query.middleware(UserExistenceCheckMiddleware(session_maker))


if __name__ == "__main__":
    try:
        print("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been turned off")
