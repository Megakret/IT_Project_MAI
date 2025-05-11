from api.gpt.GptCommandSuggest import GptCommand
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from tg_bot.routers.add_place_handler import geosuggest_test
from tg_bot.routers.place_list_handlers import show_place_list
from tg_bot.routers.user_place_list_handler import show_user_place_list
from tg_bot.routers.get_place_info_handler import get_place_handler
from tg_bot.routers.get_places_by_tag_handler import show_tag_menu_handler
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
suggester = GptCommand()


@router.message()
async def perform_action(message: Message, state: FSMContext, session: AsyncSession):
    command = await suggester.command_NAC(message.text)
    match command:
        case "/add_place":
            await message.answer(f"Выполняется команда: {command}")
            await geosuggest_test(message, state)
        case "/place_list":
            await message.answer(f"Выполняется команда: {command}")
            await show_place_list(message, state, session)
        case "/user_place_list":
            await message.answer(f"Выполняется команда: {command}")
            await show_user_place_list(message, state, session)
        case "/get_place":
            await message.answer(f"Выполняется команда: {command}")
            await get_place_handler(message, state)
        case "/place_by_tag":
            await message.answer(f"Выполняется команда: {command}")
            await show_tag_menu_handler(message, state, session)
        case _:
            await message.answer("Команда не найдена.")
