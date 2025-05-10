from typing import Awaitable, Dict, Any, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker


class DatabaseConnectionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self._session_maker() as session:
            data["session"] = session
            return await handler(event, data)
