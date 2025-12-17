from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError

from ..entities import Permission, RoleWithPermissions
from ..entities import Role as RoleEntity
from ..models import Role as Role
from ..schemas import CreateRoleDTO, ReplaceRoleDTO, UpdateRoleDTO


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dto: CreateRoleDTO) -> RoleEntity:
        insert_values = dto.model_dump(exclude_none=True)
        stmt = insert(Role).values(**insert_values).returning(Role)
        try:
            result = await self.db.execute(stmt)
            row = result.scalar_one()
            await self.db.commit()
            return self._to_entity(row)
        except IntegrityError as e:
            await self.db.rollback()
            raise ResourceAlreadyExistsError("Role", dto.name) from e
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError("Failed to create role") from e

    async def get_all(self) -> list[RoleEntity]:
        stmt = select(Role.id, Role.name, Role.description)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, id: int) -> RoleEntity | None:
        stmt = select(Role.id, Role.name, Role.description).where(Role.id == id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def get_by_name(self, name: str) -> RoleEntity | None:
        stmt = select(Role.id, Role.name, Role.description).where(Role.name == name)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_entity(row)

    async def update(self, id: int, data: UpdateRoleDTO | ReplaceRoleDTO) -> RoleEntity | None:
        update_values: dict[str, Any] = data.model_dump(exclude_none=True)

        if not update_values:
            raise ValueError("No fields provided for update")

        stmt = update(Role).where(Role.id == id).values(**update_values).returning(Role)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        await self.db.commit()
        return self._to_entity(row)

    async def delete(self, id: int) -> RoleEntity | None:
        stmt = delete(Role).where(Role.id == id).returning(Role)
        try:
            result = await self.db.execute(stmt)
            await self.db.commit()
            row = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to delete role with id={id}") from e
        if row is None:
            return None
        return self._to_entity(row)

    async def get_with_permissions(self, id: int) -> RoleWithPermissions | None:
        stmt = select(Role).where(Role.id == id).options(selectinload(Role.permissions))
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        permissions = [
            Permission(id=p.id, name=p.name, description=p.description) for p in row.permissions
        ]
        return RoleWithPermissions(
            id=row.id, name=row.name, description=row.description, permissions=permissions
        )

    async def add_permissions(
        self, id: int, permission_ids: list[int]
    ) -> RoleWithPermissions | None:
        from ..models import Permission as PermissionModel
        from ..models import role_permissions

        role_stmt = select(Role.id).where(Role.id == id)
        role_result = await self.db.execute(role_stmt)
        if role_result.scalar_one_or_none() is None:
            raise ResourceNotFoundError("Role", id)

        stmt = select(PermissionModel.id).where(PermissionModel.id.in_(permission_ids))
        result = await self.db.execute(stmt)
        found_ids = set(result.scalars().all())

        missing_ids = set(permission_ids) - found_ids
        if missing_ids:
            raise ValueError(f"Permissions not found: {missing_ids}")

        from sqlalchemy.dialects.postgresql import insert as pg_insert

        values = [{"role_id": id, "permission_id": perm_id} for perm_id in permission_ids]
        insert_stmt = pg_insert(role_permissions).values(values).on_conflict_do_nothing()
        await self.db.execute(insert_stmt)
        await self.db.commit()

        return await self.get_with_permissions(id)

    def _to_entity(self, model: Role) -> RoleEntity:
        return RoleEntity(id=model.id, name=model.name, description=model.description)

    def _from_entity(self, entity: RoleEntity) -> Role:
        return Role(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )
