import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

engine: AsyncEngine
async_session_maker: async_sessionmaker

from database.db_tables import *
from database.db_user_functions import *
from database.db_place_functions import *
from database.db_user_place_functions import *
from database.db_place_tags_functions import *
from database.db_requests_functions import *
from database.db_channels_functions import *


def init_database() -> async_sessionmaker:
    global engine
    engine = create_async_engine("sqlite+aiosqlite:///src/database/database.db")
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return async_session_maker


async def async_main() -> None:
    init_database()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(async_main())
