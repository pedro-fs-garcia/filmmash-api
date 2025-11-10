from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core import get_settings, register_exception_handlers
from app.core.logger import get_logger
from app.core.middleware import add_middlewares
from app.db import close_postgres_db, init_postgres_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger()
    settings = get_settings()
    logger.info("Starting Application...")

    try:
        if settings.ENVIRONMENT == "development":
            await init_postgres_db()
        yield

    finally:
        logger.info("🛑 Shutting Down Application...")
        await close_postgres_db()
        logger.stop()


def initiate_routers(app: FastAPI) -> None:
    app.include_router(api_router, prefix="/api")

    @app.get("/", tags=["Health Check"])
    def read_root() -> dict[str, str]:  # type:ignore
        """root endpoint to verify if the API is running."""
        return {"name": app.title, "status": "ok", "environment": get_settings().ENVIRONMENT}


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    add_middlewares(app)
    initiate_routers(app)
    register_exception_handlers(app)
    return app
