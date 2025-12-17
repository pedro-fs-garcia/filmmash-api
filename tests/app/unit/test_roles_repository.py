import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.repositories.role_repository import RoleRepository
from app.domains.auth.schemas import CreateRoleDTO


class TestCreateRoleDTO:
    @pytest.mark.asyncio
    async def test_create_role_dto_with_empty_name_should_fail(self) -> None:
        with pytest.raises(ValidationError):
            dto = CreateRoleDTO(name="", description="A test role")
            assert not dto

    @pytest.mark.asyncio
    async def test_create_role_dto_with_none_name_should_fail(self) -> None:
        with pytest.raises(ValueError):
            dto = CreateRoleDTO(name=None, description="A test role")
            assert not dto

    @pytest.mark.asyncio
    async def test_create_role_dto_with_short_name_should_fail(self) -> None:
        with pytest.raises(ValidationError):
            dto = CreateRoleDTO(name="A", description="A test role")
            assert not dto

    @pytest.mark.asyncio
    async def test_create_role_dto_with_description_none(self) -> None:
        dto = CreateRoleDTO(name="test_role")
        assert dto.name == "test_role"
        assert dto.description is None

    @pytest.mark.asyncio
    async def test_create_role_dto_with_valid_data(self) -> None:
        dto = CreateRoleDTO(name="test_role", description="A test role")
        assert dto.name == "test_role"
        assert dto.description == "A test role"


class TestRolesRepository:
    """Unit tests for RoleRepository."""

    @pytest.fixture
    def role_repo(self, db_session: AsyncSession) -> RoleRepository:
        """Create a RoleRepository instance for each test."""
        return RoleRepository(db=db_session)

    @pytest.mark.asyncio
    async def test_create_role_success(self, role_repo: RoleRepository) -> None:
        dto = CreateRoleDTO(name="test_role", description="A test role")
        role = await role_repo.create(dto)
        assert role is not None
        assert role.name == dto.name
        assert role.description == dto.description
