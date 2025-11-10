from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import async_session


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db_session:
        yield db_session
