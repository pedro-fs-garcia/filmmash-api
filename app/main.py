import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core import get_settings, register_exception_handlers
from app.core.background_tasks import global_background_tasks
from app.core.logger import get_logger
from app.core.metrics import metrics_router
from app.core.middleware import add_middlewares
from app.db import close_postgres_db, init_postgres_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger()
    settings = get_settings()
    logger.info("Starting Application...")
    tasks = global_background_tasks()

    try:
        if settings.ENVIRONMENT == "development":
            await init_postgres_db()

        yield

    finally:
        logger.info("🛑 Shutting Down Application...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await close_postgres_db()
        logger.stop()


def initiate_routers(app: FastAPI) -> None:
    settings = get_settings()
    app.include_router(api_router, prefix="/api")
    app.include_router(metrics_router)

    @app.get("/", tags=["Health Check"])
    async def read_root() -> dict[str, str]:
        """root endpoint to verify if the API is running."""
        return {"name": app.title, "status": "ok", "environment": settings.ENVIRONMENT}


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
