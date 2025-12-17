from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db.postgres.dependencies import get_postgres_session
from app.main import create_app

settings = get_settings()


@pytest.fixture
def async_engine() -> AsyncEngine:
    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
    )
    return engine


@pytest.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncSession | Any:
    async with async_engine.connect() as conn:
        trans = await conn.begin()

        async_session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )

        async with async_session() as session:
            yield session

        await trans.rollback()


@pytest.fixture(scope="module")
def app() -> FastAPI:
    app = create_app()
    return app


@pytest.fixture(scope="module")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient connected to the FastAPI test app."""
    app.dependency_overrides[get_postgres_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
