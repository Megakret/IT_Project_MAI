from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from tg_bot.keyboards import get_user_keyboard
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tg_bot.routers.get_places_by_tag_handler import router as get_places_by_tag_router
from tg_bot.routers.add_place_handler import router as add_place_router
from tg_bot.routers.place_list_handlers import router as place_list_router
from tg_bot.routers.user_place_list_handler import router as user_place_list_router
from tg_bot.routers.get_place_info_handler import router as get_place_info_router
from tg_bot.routers.gpt_talk_handlers import router as gpt_router
from tg_bot.middlewares.UserExistenceCheckMiddleware import UserExistenceCheckMiddleware

router = Router()


def initialize_user_routers(session_maker: async_sessionmaker):
    router.include_router(add_place_router)
    router.include_router(place_list_router)
    router.include_router(user_place_list_router)
    router.include_router(get_place_info_router)
    router.include_router(gpt_router)
    router.include_router(get_places_by_tag_router)
    router.message.middleware(UserExistenceCheckMiddleware(session_maker))
    router.callback_query.middleware(UserExistenceCheckMiddleware(session_maker))


@router.message(Command("exit"))
async def exit_command(message: Message, state: FSMContext, session: AsyncSession):
    current_state: State = await state.get_state()
    if current_state is None:
        await message.answer("Вы итак в главном меню")
    else:
        await message.answer(
            "Вы вышли в главное меню",
            reply_markup=(await get_user_keyboard(session, message.from_user.id)),
        )
        await state.set_state(None)
