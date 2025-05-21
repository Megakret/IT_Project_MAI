import sqlite3
from sqlalchemy import delete, exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .db_tables import User, Place, UserPlace
from .db_exceptions import UniqueConstraintError, ConstraintError


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


async def get_user_place(
    session: AsyncSession, address: str, user_id: int
) -> UserPlace:
    statement = (
        select(UserPlace)
        .where(UserPlace.fk_user_id == user_id, UserPlace.fk_place_address == address)
    )
    result = await session.execute(statement)
    review: UserPlace | None = result.scalar_one_or_none()
    if not review:
        raise ValueError("UserPlace was not found")
    return review


async def is_existing_user_place(
    session: AsyncSession, address: str, user_id: int
) -> bool:
    statement = select(
        exists().where(
            UserPlace.fk_place_address == address, UserPlace.fk_user_id == user_id
        )
    )
    is_existing = await session.execute(statement)
    return is_existing.scalar_one()


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


async def get_place_comments(
    session: AsyncSession, page: int, comments_per_page: int, address: str
) -> list[tuple[str, str, int]]:
    statement = (
        select(User.name, UserPlace.comment, UserPlace.score)
        .join(User, User.id == UserPlace.fk_user_id)
        .where(UserPlace.fk_place_address == address, UserPlace.comment.is_not(None))
        .order_by(UserPlace.score.desc())
        .limit(comments_per_page)
        .offset((page - 1) * comments_per_page)
    )

    result = await session.execute(statement)
    comments = result.all()
    return [
        (username, comment, score)
        for username, comment, score in comments
        if comment is not None
    ]


async def get_comments_of_user(
    session: AsyncSession, page: int, comments_per_page: int, username: str
) -> list[tuple[Place, str, int]]:
    statement = (
        select(UserPlace.comment, UserPlace.score, Place)
        .join(User, User.id == UserPlace.fk_user_id)
        .join(Place, Place.address == UserPlace.fk_place_address)
        .where(User.name == username, UserPlace.comment.is_not(None))
        .order_by(UserPlace.score.desc())
        .limit(comments_per_page)
        .offset((page - 1) * comments_per_page)
    )

    result = await session.execute(statement)
    comments = result.all()
    return [
        (place_data, comment, score)
        for comment, score, place_data in comments
        if comment is not None
    ]


async def get_place_comments_all(
    session: AsyncSession, address: str
) -> list[tuple[int, str | None]]:
    statement = select(UserPlace.fk_user_id, UserPlace.comment).where(
        UserPlace.fk_place_address == address, UserPlace.comment.is_not(None)
    )
    result = await session.execute(statement)
    return list(result.tuples())


async def user_has_comment(
    session: AsyncSession, user_id: int, place_address: str
) -> bool:
    comment_exists = await session.execute(
        select(
            exists().where(
                UserPlace.fk_user_id == user_id,
                UserPlace.fk_place_address == place_address,
                UserPlace.comment.is_not(None),
            )
        )
    )

    return comment_exists.scalar_one()


async def remove_review(session: AsyncSession, username: str, place_id: int) -> None:
    statement = (
        delete(UserPlace)
        .where(
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
        .returning(UserPlace.fk_user_id)
    )
    result = (await session.execute(statement)).scalar_one_or_none()
    print(result)
    if not result:
        raise ValueError("User comment not found")
    await session.commit()
