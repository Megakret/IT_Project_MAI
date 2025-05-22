import sqlite3
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.db_exceptions import UniqueConstraintError, ConstraintError
from database.db_tables import User


async def get_id_by_username(session: AsyncSession, username: str) -> int:
    statement = select(User.id).where(User.name == username)
    result = (await session.execute(statement=statement)).scalar_one_or_none()
    if not result:
        raise ValueError("Username is not found")
    return result


async def add_user(
    session: AsyncSession,
    id: int,
    name: str,
    rights: int | None = 1,
    is_banned: bool | None = False,
) -> None:
    try:
        session.add(
            User(
                id=id,
                name=name,
                rights=rights,
                is_banned=is_banned,
            )
        )
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(["id"], [str(id)])
            else:
                raise ConstraintError(["id"], [str(id)])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def delete_user(session: AsyncSession, user_id: int) -> None:
    usr = session.get(User, user_id)
    if usr is None:
        raise ValueError(f"User with ID {user_id} not found")
    await session.delete(usr)
    await session.commit()


async def does_user_exist(session: AsyncSession, username: str) -> bool:
    result = (
        await session.execute(statement=select(User.name).where(User.name == username))
    ).scalar_one_or_none()
    return bool(result)


async def delete_user_data_by_username(session: AsyncSession, username: str) -> None:
    user_data = await session.execute(select(User.id).where(User.name == username))
    id = user_data.scalar_one_or_none()
    if not id:
        raise ValueError(f"User with username {username} not found")
    await delete_user(session, id)
    await add_user(session, id, username, 1, True)
    await session.commit()


async def is_existing_user(session: AsyncSession, id: int) -> bool:
    statement = select(exists().where(User.id == id))
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


async def get_users_by_permission(
    session: AsyncSession, page: int, places_per_page: int, permission: int
) -> list[str]:

    if permission < 3:
        statement = (
            select(User.name)
            .where(User.rights == permission, User.is_banned == False)
            .order_by(User.name)
            .limit(places_per_page)
            .offset((page - 1) * places_per_page)
        )
    else:
        statement = (
            select(User.name)
            .where(User.rights >= permission, User.is_banned == False)
            .order_by(User.name)
            .limit(places_per_page)
            .offset((page - 1) * places_per_page)
        )

    result = await session.execute(statement)
    instance_list = list(result.scalars().all())
    return instance_list


async def get_banned_users(
    session: AsyncSession, page: int, places_per_page: int
) -> list[str]:
    statement = (
        select(User.name)
        .where(User.is_banned == True)
        .order_by(User.name)
        .limit(places_per_page)
        .offset((page - 1) * places_per_page)
    )
    result = await session.execute(statement)
    instance_list = list(result.scalars().all())
    return instance_list


async def get_permisions(session: AsyncSession, id: int) -> int:
    result = await session.execute(statement=select(User.rights).where(User.id == id))
    return result.scalar_one()


async def is_manager(session: AsyncSession, id: int) -> bool:
    return (await get_permisions(session, id)) >= 2


async def get_user_rights(session: AsyncSession, id: int) -> int:
    result = await session.execute(statement=select(User.rights).where(User.id == id))
    return result.scalar_one()


async def is_admin(session: AsyncSession, id: int) -> bool:
    return (await get_permisions(session, id)) >= 3


async def is_owner(session: AsyncSession, id: int) -> bool:
    return (await get_permisions(session, id)) == 4


async def make_user(session: AsyncSession, username: str) -> None:
    result = await session.execute(select(User).where(User.name == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(f"User '{username}' not found")
    user.rights = 1
    await session.commit()


async def make_manager(session: AsyncSession, username: str) -> None:
    result = await session.execute(select(User).where(User.name == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(f"User '{username}' not found")
    user.rights = 2
    await session.commit()


async def make_admin(session: AsyncSession, username: str) -> None:
    result = await session.execute(select(User).where(User.name == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(f"User '{username}' not found")
    user.rights = 3
    await session.commit()


async def ban(session: AsyncSession, id: int) -> None:
    await session.execute(
        statement=update(User).where(User.id == id).values(is_banned=True, rights=1)
    )


async def ban_by_username(session: AsyncSession, username: str) -> None:
    await session.execute(
        statement=update(User)
        .where(User.name == username)
        .values(is_banned=True, rights=1)
    )
    await session.commit()


async def unban(session: AsyncSession, id: int) -> None:
    await session.execute(
        statement=update(User).where(User.id == id).values(is_banned=False)
    )
    await session.commit()


async def unban_by_username(session: AsyncSession, username: str) -> None:
    await session.execute(
        statement=update(User).where(User.name == username).values(is_banned=0)
    )
    await session.commit()


async def is_user_banned(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(User.is_banned).where(User.id == user_id))
    banned_status = result.scalar_one_or_none()

    if banned_status is None:
        return False
    return banned_status


async def is_username_banned(session: AsyncSession, username: str) -> bool:
    result = await session.execute(select(User.is_banned).where(User.name == username))
    banned_status = result.scalar_one_or_none()

    if banned_status is None:
        return False
    return banned_status
