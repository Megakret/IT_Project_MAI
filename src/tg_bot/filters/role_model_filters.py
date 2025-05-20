from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_functions import get_user_rights, is_admin


class IsManager(Filter):

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user_rights: int = await get_user_rights(session, message.from_user.id)
        return user_rights >= 2


class IsAdmin(Filter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        return await is_admin(session, message.from_user.id)
