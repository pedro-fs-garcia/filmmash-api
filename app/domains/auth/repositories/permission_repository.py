from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError

from ..entities import Permission as PermissionEntity
from ..entities import PermissionWithRoles, Role
from ..models import Permission as PermissionModel
from ..schemas import CreatePermissionDTO, ReplacePermissionDTO, UpdatePermissionDTO


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dto: CreatePermissionDTO) -> PermissionEntity:
        insert_values = dto.model_dump(exclude_none=True)
        stmt = insert(PermissionModel).values(**insert_values).returning(PermissionModel)
        try:
            result = await self.db.execute(stmt)
            row = result.scalar_one()
            await self.db.commit()
            return self._to_entity(row)
        except IntegrityError as e:
            await self.db.rollback()
            raise ResourceAlreadyExistsError("Permission", dto.name) from e
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError("Failed to create permission") from e

    async def get_all(self) -> list[PermissionEntity]:
        stmt = select(PermissionModel.id, PermissionModel.name, PermissionModel.description)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, id: int) -> PermissionEntity | None:
        stmt = select(PermissionModel.id, PermissionModel.name, PermissionModel.description).where(
            PermissionModel.id == id
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def update(
        self, id: int, dto: UpdatePermissionDTO | ReplacePermissionDTO
    ) -> PermissionEntity | None:
        update_values: dict[str, Any] = dto.model_dump(exclude_none=True)
        if not update_values:
            raise ValueError("No fields provided for update")
        stmt = (
            update(PermissionModel)
            .where(PermissionModel.id == id)
            .values(**update_values)
            .returning(PermissionModel)
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        await self.db.commit()
        return self._to_entity(row)

    async def delete(self, id: int) -> PermissionEntity | None:
        stmt = delete(PermissionModel).where(PermissionModel.id == id).returning(PermissionModel)
        try:
            result = await self.db.execute(stmt)
            await self.db.commit()
            row = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to delete permission with id={id}") from e
        if row is None:
            return None
        return self._to_entity(row)

    async def get_with_roles(self, id: int) -> PermissionWithRoles | None:
        stmt = (
            select(PermissionModel)
            .where(PermissionModel.id == id)
            .options(selectinload(PermissionModel.roles))
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        roles = [Role(id=r.id, name=r.name, description=r.description) for r in row.roles]
        return PermissionWithRoles(
            id=row.id, name=row.name, description=row.description, roles=roles
        )

    async def add_to_roles(self, id: int, role_ids: list[int]) -> PermissionWithRoles | None:
        from ..models import Role as Role
        from ..models import role_permissions

        permission_stmt = select(PermissionModel.id).where(PermissionModel.id == id)
        permission_res = await self.db.execute(permission_stmt)
        if permission_res.scalar_one_or_none() is None:
            raise ResourceNotFoundError("Permission", id)

        stmt = select(Role.id).where(Role.id.in_(role_ids))
        result = await self.db.execute(stmt)
        found_ids = set(result.scalars().all())

        missing_ids = set(role_ids) - found_ids
        if missing_ids:
            raise ValueError(f"Roles not found: {missing_ids}")

        from sqlalchemy.dialects.postgresql import insert as pg_insert

        values = [{"permission_id": id, "role_id": role_id} for role_id in role_ids]
        insert_stmt = pg_insert(role_permissions).values(values).on_conflict_do_nothing()
        await self.db.execute(insert_stmt)
        await self.db.commit()

        return await self.get_with_roles(id)

    def _to_entity(self, model: PermissionModel) -> PermissionEntity:
        return PermissionEntity(id=model.id, name=model.name, description=model.description)
