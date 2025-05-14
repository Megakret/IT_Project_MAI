import asyncio
import sqlite3
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    UniqueConstraint,
    delete,
    exists,
    func,
    select,
    update,
)
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
    global engine
    engine = create_async_engine(
        "sqlite+aiosqlite:///src/database/database.db", echo=True
    )
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return async_session_maker


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(unique=True)
    rights: Mapped[int] = mapped_column(CheckConstraint("rights BETWEEN 1 and 3"))
    is_banned: Mapped[bool]

    user_places: Mapped[list["UserPlace"]] = relationship(
        back_populates="parent_user", cascade="all, delete-orphan"
    )


class Place(Base):
    __tablename__ = "place"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    address: Mapped[str] = mapped_column(unique=True)
    desc: Mapped[str | None]

    user_places: Mapped[list["UserPlace"]] = relationship(
        back_populates="parent_place", cascade="all, delete-orphan"
    )
    place_tags: Mapped[list["Tag"]] = relationship(
        back_populates="parent_place", cascade="all, delete-orphan"
    )


class Requests(Base):
    __tablename__ = "requests"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    name: Mapped[str]
    address: Mapped[str] = mapped_column(unique=True)
    desc: Mapped[str | None]

    __mapper_args__ = {"primary_key": [fk_user_id, address]}


class UserPlace(Base):
    __tablename__ = "user_place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    score: Mapped[int | None] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"))
    comment: Mapped[str | None]

    parent_user: Mapped["User"] = relationship(back_populates="user_places")
    parent_place: Mapped["Place"] = relationship(back_populates="user_places")

    UniqueConstraint(fk_user_id, fk_place_address)

    __mapper_args__ = {"primary_key": [fk_user_id, fk_place_address]}


class Tag(Base):
    __tablename__ = "tag"

    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    place_tag: Mapped[str] = mapped_column()

    parent_place: Mapped["Place"] = relationship(back_populates="place_tags")

    UniqueConstraint(fk_place_address, place_tag)

    __mapper_args__ = {"primary_key": [fk_place_address, place_tag]}


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


async def is_existing_user(session: AsyncSession, id: int) -> bool:
    statement = select(exists().where(User.id == id))
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


async def is_manager(session: AsyncSession, id: int) -> bool:
    result = await session.execute(statement=select(User.rights).where(User.id == id))
    return result.scalar_one() >= 2


async def is_admin(session: AsyncSession, id: int) -> bool:
    result = await session.execute(statement=select(User.rights).where(User.id == id))
    return result.scalar_one() == 3


async def ban(session: AsyncSession, id: int) -> None:
    await session.execute(
        statement=update(User).where(User.id == id).values(is_banned=True)
    )


async def unban(session: AsyncSession, id: int) -> None:
    await session.execute(
        statement=update(User).where(User.id == id).values(is_banned=False)
    )


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


async def is_existing_place(session: AsyncSession, address: str) -> bool:
    statement = select(exists().where(Place.address == address))
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


async def remove_place(session: AsyncSession, address: str) -> None:
    await session.execute(statement=delete(Place).where(Place.address == address))


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
    tags_list = result.one().tuple()
    return tags_list


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
                raise ConstraintError(["user_id", "address"], [str(user_id), address])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()


async def add_comment(
    session: AsyncSession,
    user_id: int,
    address: str,
    comment: str,
) -> None:
    try:
        statement = (
            update(UserPlace)
            .where(
                UserPlace.fk_user_id == user_id,
                UserPlace.fk_place_address == address,
            )
            .values(comment=comment)
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
                raise ConstraintError(["user_id", "address"], [str(user_id), address])
        else:
            raise
    except:
        await session.rollback()
        raise
    else:
        await session.commit()

# TODO: I need username which starts with @, not plain integer user id
async def get_place_comments(
    session: AsyncSession, page: int, comments_per_page: int, address: str
) -> list[tuple[int, str | None]]:
    statement = (
        select(UserPlace.fk_user_id, UserPlace.comment)
        .where(UserPlace.fk_place_address == address, UserPlace.comment.is_not(None))
        .limit(comments_per_page)
        .offset((page - 1) * comments_per_page)
    )
    result = await session.execute(statement)
    return list(result.tuples())


async def get_place_comments_all(
    session: AsyncSession, address: str
) -> list[tuple[int, str | None]]:
    statement = select(UserPlace.fk_user_id, UserPlace.comment).where(
        UserPlace.fk_place_address == address, UserPlace.comment.is_not(None)
    )
    result = await session.execute(statement)
    return list(result.tuples())


async def add_user_place(
    session: AsyncSession,
    user_id: int,
    address: str,
    score: int | None = None,
    comment: str | None = None,
) -> None:
    try:
        session.add(
            UserPlace(fk_user_id=user_id, fk_place_address=address, score=score)
        )
        await session.flush()
        if score:
            await rate(session, user_id, address, score)
            await session.flush()
        if comment:
            await add_comment(session, user_id, address, comment)
            await session.flush()
    except IntegrityError as error:
        await session.rollback()
        if isinstance(error.orig, sqlite3.IntegrityError):
            if error.orig.sqlite_errorcode == 2067:
                raise UniqueConstraintError(
                    ["user_id", "address"], [str(user_id), address]
                )
            else:
                raise ConstraintError(["user_id", "address"], [str(user_id), address])
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


async def get_place_with_score(
    session: AsyncSession, address: str
) -> tuple[Place, float | None]:
    statement = (
        select(Place, func.avg(UserPlace.score))
        .outerjoin(UserPlace, Place.address == UserPlace.fk_place_address)
        .where(Place.address == address)
        .group_by(Place.address)
    )
    result = await session.execute(statement)
    instance_with_score = result.one().tuple()
    return instance_with_score


async def remove_review(session: AsyncSession, username: str, place_id: int) -> None:
    statement = delete(UserPlace).where(
        UserPlace.fk_user_id
        == (
            (
                await session.execute(
                    statement=select(User.id).where(User.name == username)
                )
            ).scalar_one()
        ),
        UserPlace.fk_place_address
        == (
            (
                await session.execute(
                    statement=select(Place.address).where(Place.id == place_id)
                )
            ).scalar_one()
        ),
    )
    await session.execute(statement)


async def async_main() -> None:
    init_database()
    print(engine.url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(async_main())
