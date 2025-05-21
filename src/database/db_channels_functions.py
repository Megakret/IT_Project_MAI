import sqlite3
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.db_tables import User, TelegramChannel
from database.db_exceptions import UniqueConstraintError, ConstraintError


async def add_channel(session: AsyncSession, channel_username: str, user_id: int):
    try:
        session.add(
            TelegramChannel(channel_username=channel_username, fk_user_id=user_id)
        )
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(["channel_username"], [channel_username])
            else:
                raise ConstraintError(["channel_username"], [channel_username])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


# returns pair of channel_username username of person who added channel
async def get_paged_channels(
    session: AsyncSession, page: int, channels_per_page: int
) -> list[tuple[str, str]]:
    statement = (
        select(TelegramChannel.channel_username, User.name)
        .join(User, User.id == TelegramChannel.fk_user_id)
        .limit(channels_per_page)
        .offset((page - 1) * channels_per_page)
    )
    result = await session.execute(statement)
    instance_list = [row.tuple() for row in result.all()]
    return instance_list


async def delete_channel(session: AsyncSession, channel_username: str):
    statement = (
        delete(TelegramChannel)
        .where(TelegramChannel.channel_username == channel_username)
        .returning(TelegramChannel.id)
    )
    result = await session.execute(statement)
    if result.scalar_one_or_none is None:
        raise ValueError("This channel is not added")
    await session.commit()


async def does_channel_exist(session: AsyncSession, channel_username: str) -> bool:
    statement = select(
        exists(TelegramChannel).where(
            TelegramChannel.channel_username == channel_username
        )
    )
    result = await session.execute(statement)
    return result.scalar_one()
