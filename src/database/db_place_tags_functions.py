import sqlite3
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from .db_tables import Place, Tag
from .db_exceptions import UniqueConstraintError, ConstraintError


async def add_place_tag(session: AsyncSession, address: str, place_tag: str) -> None:
    try:
        session.add(
            Tag(
                fk_place_address=address,
                place_tag=place_tag,
            )
        )
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["address", "place_tag"], [address, place_tag]
                )
            else:
                raise ConstraintError(["address", "place_tag"], [address, place_tag])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def add_place_tags(
    session: AsyncSession, address: str, place_tags: tuple[str]
) -> None:
    try:
        await session.execute(
            delete(Tag).where(Tag.fk_place_address == address)
        )  # deleting old tags
        await session.flush()
        instances_to_add = [
            Tag(fk_place_address=address, place_tag=tag) for tag in place_tags
        ]
        session.add_all(instances_to_add)
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["address", "place_tags"], [address, *place_tags]
                )
            else:
                raise ConstraintError(["address", "place_tags"], [address, *place_tags])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def get_place_tags(session: AsyncSession, address: str) -> tuple[str]:
    statement = select(Tag.place_tag).where(Tag.fk_place_address == address)
    result = await session.execute(statement)
    tag_list = result.tuples().one()
    return tag_list
