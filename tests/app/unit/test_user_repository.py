from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.enums import OAuthProvider
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.schemas import CreateUserDTO


class TestCreateUserDTO:
    def test_create_user_with_password_and_username(self) -> None:
        dto = CreateUserDTO(
            email="user@example.com",
            password_hash="hashed-password",
            username="testuser",
            name="Test User",
        )
        assert dto.password_hash is not None
        assert dto.username == "testuser"

    def test_create_user_with_oauth(self) -> None:
        dto = CreateUserDTO(
            email="user@example.com",
            oauth_provider=OAuthProvider.GOOGLE,
            oauth_provider_id="google-123",
            name="OAuth User",
        )
        assert dto.oauth_provider == OAuthProvider.GOOGLE
        assert dto.oauth_provider_id == "google-123"

    def test_create_user_without_password_and_oauth_should_fail(self) -> None:
        with pytest.raises(ValidationError) as exc:
            CreateUserDTO(
                email="user@example.com",
                username="testuser",
                name="Test User",
            )
        assert "User must have either password or OAuth provider" in str(exc.value)

    def test_create_user_with_password_but_without_username_should_fail(self) -> None:
        with pytest.raises(ValidationError) as exc:
            CreateUserDTO(
                email="user@example.com",
                password_hash="hashed-password",
                name="Test User",
            )
        assert "User must have a name" in str(exc.value)

    def test_create_user_with_oauth_without_provider_id_should_fail(self) -> None:
        with pytest.raises(ValidationError):
            CreateUserDTO(
                email="user@example.com",
                oauth_provider=OAuthProvider.GOOGLE,
                name="OAuth User",
            )


class TestUserRepository:
    """Unit tests for UserRepository."""

    @pytest.fixture
    def user_repo(self, db_session: AsyncSession) -> UserRepository:
        """Create a UserRepository instance for each test."""
        return UserRepository(db=db_session)

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repo: UserRepository) -> None:
        dto = CreateUserDTO(
            email=f"test_{uuid4().hex[:8]}@example.com",
            username=f"testuser_{uuid4().hex[:8]}",
            name="Test User",
            password_hash="hashed_password_here",
            oauth_provider=OAuthProvider.LOCAL,
        )
        user = await user_repo.create(dto)
        assert user is not None
        assert user.email == dto.email
        assert user.username == dto.username
        assert user.name == dto.name
        assert user.is_active is True
        assert user.is_verified is False
