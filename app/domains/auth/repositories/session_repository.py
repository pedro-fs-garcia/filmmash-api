from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.exceptions import ResourceAlreadyExistsError
from app.domains.auth.enums import SessionStatus

from ..entities import Session as SessionEntity
from ..models import Session as SessionModel
from ..schemas import CreateSessionDTO, SessionDeviceInfo, UpdateSessionDTO


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dto: CreateSessionDTO) -> SessionEntity:
        insert_values = dto.model_dump(exclude_none=True)
        stmt = insert(SessionModel).values(**insert_values).returning(SessionModel)
        try:
            res = await self.db.execute(stmt)
            row = res.scalar_one()
            await self.db.commit()
            return self._to_entity(row)
        except IntegrityError as e:
            await self.db.rollback()
            raise ResourceAlreadyExistsError("Session", "refresh_token_hash") from e
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError("Failed to create user") from e

    async def get_all(self) -> list[SessionEntity]:
        stmt = select(SessionModel)
        res = await self.db.execute(stmt)
        rows = res.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_refresh_token_hash(self, refresh_token_hash: str) -> SessionEntity | None:
        stmt = select(SessionModel).where(SessionModel.refresh_token_hash == refresh_token_hash)
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def get_by_user_id(self, user_id: UUID) -> list[SessionEntity]:
        stmt = select(SessionModel).where(SessionModel.user_id == user_id)
        res = await self.db.execute(stmt)
        rows = res.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_active_by_user_id(self, user_id: UUID) -> list[SessionEntity]:
        stmt = select(SessionModel).where(
            SessionModel.user_id == user_id, SessionModel.status == SessionStatus.ACTIVE
        )
        res = await self.db.execute(stmt)
        rows = res.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def update(self, session_id: UUID, dto: UpdateSessionDTO) -> SessionEntity | None:
        update_values = dto.model_dump(exclude_none=True)
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(**update_values)
            .returning(SessionModel)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def revoke(self, session_id: UUID) -> SessionEntity | None:
        return await self.update(session_id, UpdateSessionDTO(status=SessionStatus.REVOKED))

    def _to_entity(self, model: SessionModel) -> SessionEntity:
        device_info = SessionDeviceInfo.model_validate(model.device_info)
        return SessionEntity(
            id=model.id,
            user_id=model.user_id,
            refresh_token_hash=model.refresh_token_hash,
            status=model.status,
            expires_at=model.expires_at,
            created_at=model.created_at,
            device_info=device_info,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            last_used_at=model.last_used_at,
        )
