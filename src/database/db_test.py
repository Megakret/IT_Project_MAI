import db_functions as db
from db_exceptions import UniqueConstraintError
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


async def main():
    session_maker = db.init_database()
    async with session_maker() as session:
        print(await db.delete_channel(session, "armane"))


if __name__ == "__main__":
    asyncio.run(main())
