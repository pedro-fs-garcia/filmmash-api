from datetime import datetime, timedelta
from uuid import UUID

from app.domains.auth.enums import SessionStatus
from app.domains.auth.exceptions import SessionExpiredError, SessionNotFoundError

from ..entities import Session
from ..repositories.session_repository import SessionRepository
from ..schemas import CreateSessionDTO, UpdateSessionDTO


class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.repo = session_repo

    async def create(self, dto: CreateSessionDTO) -> Session:
        return await self.repo.create(dto)

    async def get_all(self) -> list[Session]:
        return await self.repo.get_all()

    async def get_by_refresh_token_hash(self, refresh_token_hash: str) -> Session | None:
        return await self.repo.get_by_refresh_token_hash(refresh_token_hash)

    async def get_active_by_user_id(self, user_id: UUID) -> list[Session]:
        return await self.repo.get_active_by_user_id(user_id)

    async def get_by_user_id(self, user_id: UUID) -> list[Session]:
        return await self.repo.get_by_user_id(user_id)

    async def revoke(self, session_id: UUID) -> Session | None:
        return await self.repo.revoke(session_id)

    async def mark_used(self, session_id: UUID) -> Session | None:
        last_used_at = datetime.now()
        return await self.repo.update(session_id, UpdateSessionDTO(last_used_at=last_used_at))

    async def mark_expired(self, session_id: UUID) -> Session | None:
        return await self.repo.update(session_id, UpdateSessionDTO(status=SessionStatus.EXPIRED))

    async def refresh(
        self, session: Session, refresh_token_hash: str, time_delta: timedelta
    ) -> Session:
        if session.expires_at < datetime.now():
            raise SessionExpiredError("Session cannot be refreshed after expired.")

        update_dto = UpdateSessionDTO(
            refresh_token_hash=refresh_token_hash,
            expires_at=datetime.now() + time_delta,
            status=SessionStatus.ACTIVE,
            last_used_at=datetime.now(),
        )
        updated_session = await self.repo.update(session.id, update_dto)
        if updated_session is None:
            raise SessionNotFoundError("Session could not be refreshed.")
        return updated_session

    # async def refresh_access_token(self, refresh_token: str) -> str:

    #     session = await self.repo.get_by_refresh_token_hash(refresh_token)
    #     if session is None:
    #         raise SessionNotFoundException()

    #     if not session.is_active():
    #         raise SessionExpiredException()

    #     session.mark_used()
    #     await self.repo.save(session)

    #     return self.jwt_service.create_access_token(session.user_id)
