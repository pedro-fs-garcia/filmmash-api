from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import ResponseFactoryDep
from app.db.postgres.dependencies import PgSessionDep


class HealthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ping_postgres(self) -> bool:
        stmt = "SELECT 1"
        res = await self.db.execute(text(stmt))
        row = res.scalar_one_or_none()
        return row is not None

    async def ping_mongo(self) -> bool:
        return True


def get_health_service(db: PgSessionDep) -> HealthService:
    return HealthService(db)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]


health_router = APIRouter()


@health_router.get("/ping", tags=["Health Check"])
def ping(response: ResponseFactoryDep) -> JSONResponse:
    return response.success(data={"message": "pong"})


@health_router.get("/health", tags=["Health Check"])
async def check_health(service: HealthServiceDep, response: ResponseFactoryDep) -> JSONResponse:
    data = {}
    data["postgres_status"] = "connected" if await service.ping_postgres() else "degraded"
    return response.success(data=data, status_code=status.HTTP_200_OK)


@health_router.get("/ready", tags=["Health Check"])
async def check_ready(service: HealthServiceDep, response: ResponseFactoryDep) -> JSONResponse:
    return response.success({})
