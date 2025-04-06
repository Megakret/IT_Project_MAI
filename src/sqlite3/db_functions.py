import asyncio

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, select, update
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(unique=True, autoincrement=False)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    user_places: Mapped[list["UserPlace"]] = relationship(backref="user", cascade="all, delete-orphan")

    __mapper_args__ = {
        "primary_key": id
    }


class Place(Base):
    __tablename__ = "place"

    name: Mapped[str]
    address: Mapped[str] = mapped_column(unique=True)
    desc: Mapped[str | None]
    user_places: Mapped[list["UserPlace"]] = relationship(backref="place", cascade="all, delete-orphan")

    __mapper_args__ = {
        "primary_key": address
    }


class UserPlace(Base):
    __tablename__ = "user_place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address))
    score: Mapped[int | None] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"))

    UniqueConstraint(fk_user_id, fk_place_address)

    __mapper_args__ = {
        "primary_key": [fk_user_id, fk_place_address]
    }


engine = create_async_engine("sqlite+aiosqlite:///database.db")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def add_user(id: int, name: str, email: str, async_session_maker = async_session_maker) -> None:
    async with async_session_maker() as session:
        try:
            session.add(
                User(
                    id=id,
                    name=name,
                    email=email,
                )
            )
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise # Do smth smart instead maybe
        except:
            await session.rollback()
            raise # Fallback in case the're other errors
        else:
            await session.commit()


async def add_place(name: str, address: str, desc: str | None = None, async_session_maker = async_session_maker) -> None:
    async with async_session_maker() as session:
        try:
            session.add(
                Place(
                    name=name,
                    address=address,
                    desc=desc,
                )
            )
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


async def get_places(page: int, places_per_page: int, async_session_maker = async_session_maker) -> list[Place]:
    async with async_session_maker() as session:
        statement = select(Place).order_by(Place.name).\
            limit(places_per_page).offset((page - 1) * places_per_page)
        result = await session.execute(statement)
        instance_list = list(result.scalars().all())
    return instance_list


async def rate(user_id: int, address: str, score: int, async_session_maker = async_session_maker) -> None:
    async with async_session_maker() as session:
        try:
            statement = update(UserPlace).\
                where(UserPlace.fk_user_id == user_id, UserPlace.fk_place_address == address).\
                values(score=score)
            await session.execute(statement)
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


async def add_user_place(user_id: int, address: str, score: int | None = None, async_session_maker = async_session_maker) -> None:
    async with async_session_maker() as session:
        try:
            session.add(
                UserPlace(
                    fk_user_id=user_id,
                    fk_place_address=address,
                )
            )
            if (score):
                await rate(user_id, address, score)
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise
        except:
            await session.rollback()
            raise
        else:
            await session.commit()


async def get_user_places(page: int, places_per_page: int, user_id: int, async_session_maker = async_session_maker) -> list[UserPlace]:
    async with async_session_maker() as session:
        statement = select(UserPlace).\
            where(UserPlace.fk_user_id == user_id).\
            limit(places_per_page).\
            offset((page - 1) * places_per_page)
        result = await session.execute(statement)
        instance_list = list(result.scalars().all())
    return instance_list


async def async_main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(async_main())

