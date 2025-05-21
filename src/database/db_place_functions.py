from .db_tables import Place, Tag

import sqlite3
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from database.db_exceptions import UniqueConstraintError, ConstraintError


async def add_place(
    session: AsyncSession,
    name: str,
    address: str,
    desc: str | None = None,
) -> None:
    try:
        session.add(
            Place(
                name=name,
                address=address,
                desc=desc,
            )
        )
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(["address"], [address])
            else:
                raise ConstraintError(["address"], [address])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def update_place_description(
    session: AsyncSession, address: str, description: str
):
    result = await session.execute(
        statement=select(Place).where(Place.address == address)
    )
    place = result.scalar_one()
    place.desc = description
    await session.commit()


async def delete_place_by_address(session: AsyncSession, address: str) -> None:
    result = await session.execute(select(Place).where(Place.address == address))
    place: Place | None = result.scalar_one_or_none()

    if place is None:
        raise ValueError(f"Place with address '{address}' not found")
    await session.delete(place)
    await session.commit()


async def get_places(
    session: AsyncSession, page: int, places_per_page: int
) -> list[Place]:
    statement = (
        select(Place)
        .order_by(Place.name)
        .limit(places_per_page)
        .offset((page - 1) * places_per_page)
    )
    result = await session.execute(statement)
    instance_list = list(result.scalars().all())
    return instance_list


async def get_places_with_tag(
    session: AsyncSession, tag: str, page: int, places_per_page: int
) -> list[Place]:
    statement = (
        select(Place)
        .where(Tag.place_tag == tag, Place.address == Tag.fk_place_address)
        .limit(places_per_page)
        .offset((page - 1) * places_per_page)
    )
    result = await session.execute(statement)
    instance_list = list(result.scalars().all())
    return instance_list


async def is_existing_place(session: AsyncSession, address: str) -> bool:
    statement = select(exists().where(Place.address == address))
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


async def is_existing_place_by_id(session: AsyncSession, place_id: int) -> bool:
    statement = select(exists().where(Place.id == place_id))
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


async def remove_place(session: AsyncSession, place_id: int) -> None:
    place_exists: bool = await is_existing_place_by_id(session, place_id)
    if not place_exists:
        raise NoResultFound
    await session.delete(session.get(Place, place_id))
    await session.commit()

