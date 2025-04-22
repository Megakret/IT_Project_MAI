import asyncio
import sqlite3

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, func, select, update
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError

from database.db_exceptions import UniqueConstraintError, ConstraintError

engine: AsyncEngine
async_session_maker: async_sessionmaker


def init_database() -> async_sessionmaker:
    engine = create_async_engine("sqlite+aiosqlite:///src/database/database.db")
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return async_session_maker


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(unique=True, autoincrement=False)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    user_places: Mapped[list["UserPlace"]] = relationship(
        backref="user", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"primary_key": id}


class Place(Base):
    __tablename__ = "place"

    name: Mapped[str]
    address: Mapped[str] = mapped_column(unique=True)
    desc: Mapped[str | None]
    user_places: Mapped[list["UserPlace"]] = relationship(
        backref="place", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"primary_key": address}


class UserPlace(Base):
    __tablename__ = "user_place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    score: Mapped[int | None] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"))
    commentary: Mapped[str | None]

    UniqueConstraint(fk_user_id, fk_place_address)

    __mapper_args__ = {"primary_key": [fk_user_id, fk_place_address]}


async def add_user(session: AsyncSession, id: int, name: str, email: str) -> None:
    try:
        session.add(
            User(
                id=id,
                name=name,
                email=email,
            )
        )
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(["email"], [email])
            else:
                raise ConstraintError(["email"], [email])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


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


async def rate(
    session: AsyncSession,
    user_id: int,
    address: str,
    score: int,
) -> None:
    try:
        statement = (
            update(UserPlace)
            .where(
                UserPlace.fk_user_id == user_id,
                UserPlace.fk_place_address == address,
            )
            .values(score=score)
        )
        await session.execute(statement)
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
            else:
                raise ConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def comment(
    session: AsyncSession,
    user_id: int,
    address: str,
    commentary: str,
) -> None:
    try:
        statement = (
            update(UserPlace)
            .where(
                UserPlace.fk_user_id == user_id,
                UserPlace.fk_place_address == address,
            )
            .values(commentary=commentary)
        )
        await session.execute(statement)
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
            else:
                raise ConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def add_user_place(
    session: AsyncSession,
    user_id: int,
    address: str,
    score: int | None = None,
    commentary: str | None = None,
) -> None:
    try:
        session.add(
            UserPlace(fk_user_id=user_id, fk_place_address=address, score=score)
        )
        await session.flush()
        if (score):
            await rate(session, user_id, address, score)
        await session.flush()
        if (commentary):
            await comment(session, user_id, address, commentary)
        await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
            else:
                raise ConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def get_user_places(
    session: AsyncSession,
    page: int,
    places_per_page: int,
    user_id: int,
) -> list[tuple[Place, int | None]]:
    statement = (
        select(Place, UserPlace.score)
        .outerjoin(UserPlace, Place.address == UserPlace.fk_place_address)
        .where(UserPlace.fk_user_id == user_id)
        .limit(places_per_page)
        .offset((page - 1) * places_per_page)
    )
    result = await session.execute(statement)
    instance_list = [row.tuple() for row in result.all()]
    return instance_list


async def get_place_with_score(session: AsyncSession, address: str) -> tuple[Place, float | None]:
    statement = (
        select(Place, func.avg(UserPlace.score))
        .outerjoin(UserPlace, Place.address == UserPlace.fk_place_address)
        .where(Place.address == address)
        .group_by(Place.address)
    )
    result = await session.execute(statement)
    instance_with_score = result.one().tuple()
    return instance_with_score


async def async_main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(async_main())
