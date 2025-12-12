from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.exceptions import ResourceAlreadyExistsError

from ..entities import Role as RoleEntity
from ..entities import User as UserEntity
from ..entities import UserWithRoles
from ..models import Role as RoleModel
from ..models import User as UserModel
from ..models import user_roles
from ..schemas import CreateUserDTO, ReplaceUserDTO, UpdateUserDTO


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dto: CreateUserDTO) -> UserEntity:
        insert_values = dto.model_dump(exclude_none=True)
        stmt = insert(UserModel).values(**insert_values).returning(UserModel)
        try:
            res = await self.db.execute(stmt)
            row = res.scalar_one()
            await self.db.commit()
            return self._to_entity(row)
        except IntegrityError as e:
            await self.db.rollback()
            raise ResourceAlreadyExistsError("User", "email or username") from e
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError("Failed to create user") from e

    async def get_all(self) -> list[UserEntity]:
        result = await self.db.execute(select(UserModel))
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, id: UUID) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.id == id)
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == email)
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def get_active(self) -> list[UserEntity]:
        stmt = select(UserModel).where(UserModel.is_active)
        res = await self.db.execute(stmt)
        rows = res.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def update(self, id: UUID, dto: UpdateUserDTO | ReplaceUserDTO) -> UserEntity | None:
        update_values = dto.model_dump(exclude_none=True)
        stmt = (
            update(UserModel).where(UserModel.id == id).values(**update_values).returning(UserModel)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        await self.db.commit()
        return self._to_entity(row)

    async def soft_delete(self, id: UUID) -> UserEntity | None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == id)
            .values({"deleted_at": func.now(), "is_active": False})
            .returning(UserModel)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        await self.db.commit()
        return self._to_entity(row)

    async def hard_delete(self, id: UUID) -> UserEntity | None:
        stmt = delete(UserModel).where(UserModel.id == id).returning(UserModel)
        try:
            res = await self.db.execute(stmt)
            row = res.scalar_one_or_none()
            await self.db.commit()
            if row is None:
                return None
            return self._to_entity(row)
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to hard delete User with id = {id}.") from e

    async def get_with_roles(self, id: UUID) -> UserWithRoles | None:
        stmt = select(UserModel).where(UserModel.id == id).options(selectinload(UserModel.roles))
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        roles = [RoleEntity(id=r.id, name=r.name, description=r.description) for r in row.roles]
        return UserWithRoles(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            username=row.username,
            name=row.name,
            oauth_provider=row.oauth_provider,
            oauth_provider_id=row.oauth_provider_id,
            is_active=row.is_active,
            is_verified=row.is_verified,
            roles=roles,
        )

    async def add_roles(
        self, id: UUID, role_ids: list[int]
    ) -> tuple[UserWithRoles | None, set[int] | None]:
        user = await self.get_by_id(id)
        if user is None:
            return (None, None)

        roles_stmt = select(RoleModel.id).where(RoleModel.id.in_(role_ids))
        result = await self.db.execute(roles_stmt)
        found_ids = set(result.scalars().all())

        missing_ids = set(role_ids) - found_ids
        if missing_ids:
            return (None, missing_ids)

        from sqlalchemy.dialects.postgresql import insert as pg_insert

        vlues: list[dict[str, UUID | int]] = [
            {"user_id": id, "role_id": role_id} for role_id in role_ids
        ]
        insert_stmt = pg_insert(user_roles).values(vlues).on_conflict_do_nothing()
        await self.db.execute(insert_stmt)
        await self.db.commit()

        updated_user = await self.get_with_roles(id)
        return (updated_user, None)

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            username=model.username,
            name=model.name,
            oauth_provider=model.oauth_provider,
            oauth_provider_id=model.oauth_provider_id,
            is_active=model.is_active,
            is_verified=model.is_verified,
        )
