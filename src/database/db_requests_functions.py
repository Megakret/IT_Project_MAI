from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from .db_tables import AddPlaceRequest


async def add_place_request(
    session: AsyncSession,
    user_id: int,
    place_name: str,
    address: str,
    description: str,
    tags: list[str],
):
    session.add(
        AddPlaceRequest(
            fk_user_id=user_id,
            place_name=place_name,
            address=address,
            description=description,
            is_operated=False,
            tags_formatted="; ".join(tags),
        )
    )
    await session.commit()


# throws NoResultFound from sqlalchemy.exc if no requests
# tags_formatted may be None
async def get_first_request(session: AsyncSession) -> AddPlaceRequest:
    statement = (
        select(AddPlaceRequest).where(AddPlaceRequest.is_operated == False).limit(1)
    )
    result = await session.execute(statement)
    request = result.scalar_one()
    request.is_operated = True
    await session.commit()
    return request


# throws NoResultFound if given request is not in db (might have been deleted)
async def delete_request(session: AsyncSession, request_id: int):
    request: AddPlaceRequest | None = await session.get(AddPlaceRequest, request_id)
    if request is None:
        raise NoResultFound
    await session.delete(request)
    await session.commit()


# throws NoResultFound if given request is not in db (might have been deleted)
async def delay_add_place_request(session: AsyncSession, request_id: int):
    request = await session.get(AddPlaceRequest, request_id)
    if request is None:
        raise NoResultFound
    request.is_operated = False
    await session.commit()
