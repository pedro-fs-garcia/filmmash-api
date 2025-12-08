from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        ...

    async def get_user(self, **filters: Any) -> User | None:
        stmt = select(User).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, name: str, password_hash: str) -> User:
        new_user = User(email=email, name=name, password_hash=password_hash)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
