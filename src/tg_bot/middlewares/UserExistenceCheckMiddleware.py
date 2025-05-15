from typing import Awaitable, Dict, Any, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker
from database.db_functions import is_existing_user

ERROR_MESSAGE = "Вашего аккаунта нет в базе бота. Напишите /start."


class UserExistenceCheckMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        async with self._session_maker() as session:
            user_exists: bool = await is_existing_user(session, event.from_user.id)
        if user_exists:
            return await handler(event, data)
        print("USER DOESNT EXIST")
        if isinstance(event, Message):
            await event.answer(ERROR_MESSAGE)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(ERROR_MESSAGE)
