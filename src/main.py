import dotenv
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher
from tg_bot.handlers import router
from tg_bot.place_list_handlers import router as place_list_router
from tg_bot.gpt_talk_handlers import router as gpt_router


async def main() -> None:
    dotenv.load_dotenv()
    bot = Bot(getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(place_list_router)
    dp.include_router(gpt_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been turned off")
