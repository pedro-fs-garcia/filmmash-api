"""initial schema

Revision ID: aeca945a00f8
Revises:
Create Date: 2025-12-14 21:57:14.080863

"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "aeca945a00f8"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE FUNCTION fn_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN
                NEW.updated_at := NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TABLE roles (
            id SERIAL PRIMARY KEY,
            name VARCHAR(30) NOT NULL UNIQUE,
            description VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE permissions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE role_permissions (
            role_id INTEGER REFERENCES roles(id),
            permission_id INTEGER REFERENCES permissions(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            PRIMARY KEY (role_id, permission_id)
        );


        CREATE TYPE oauth_provider AS ENUM ('local', 'google', 'microsoft');
        CREATE TABLE users (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) NOT NULL UNIQUE,
            username VARCHAR(50) UNIQUE,
            name VARCHAR(50),
            password_hash VARCHAR(255),
            oauth_provider oauth_provider,
            oauth_provider_id VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        CREATE INDEX idx_users_email ON users (email);
        CREATE INDEX idx_users_active ON users (is_active);
        CREATE INDEX idx_users_verified ON users (is_verified);

        CREATE TRIGGER trg_users_set_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION fn_set_updated_at();

        CREATE TABLE user_roles (
            user_id uuid REFERENCES users(id),
            role_id INTEGER REFERENCES roles(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            PRIMARY KEY (user_id, role_id)
        );


        CREATE TYPE session_status AS ENUM ('active', 'expired', 'invalid', 'revoked');
        CREATE TABLE sessions (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            refresh_token_hash VARCHAR(255) NOT NULL UNIQUE,
            status session_status NOT NULL DEFAULT 'active',
            device_info JSONB NOT NULL DEFAULT '{}',
            expires_at TIMESTAMP NOT NULL,
            last_used_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP,
            revoked_at TIMESTAMP,
            user_id uuid REFERENCES users(id) NOT NULL
        );
        CREATE INDEX idx_sessions_user_id_status ON sessions (user_id, status);
        CREATE INDEX idx_sessions_refresh_token_hash ON sessions (refresh_token_hash);

        CREATE TRIGGER trg_session_set_updated_at
        BEFORE UPDATE ON sessions
        FOR EACH ROW
        EXECUTE FUNCTION fn_set_updated_at();

        CREATE OR REPLACE FUNCTION set_session_revoked_at()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.status = 'revoked' AND OLD.status != 'revoked' THEN
                NEW.revoked_at := NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_session_set_revoked_at
        BEFORE UPDATE ON sessions
        FOR EACH ROW
        EXECUTE FUNCTION set_session_revoked_at();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_session_set_revoked_at ON sessions;")
    op.execute("DROP FUNCTION IF EXISTS set_session_revoked_at;")
    op.execute("DROP TRIGGER IF EXISTS trg_session_set_updated_at ON sessions;")
    op.execute("DROP INDEX IF EXISTS idx_sessions_refresh_token_hash;")
    op.execute("DROP INDEX IF EXISTS idx_sessions_user_id;")
    op.execute("DROP TABLE IF EXISTS sessions CASCADE;")
    op.execute("DROP TYPE IF EXISTS session_status CASCADE;")
    op.execute("DROP TABLE IF EXISTS user_roles CASCADE;")
    op.execute("DROP TRIGGER IF EXISTS trg_users_set_updated_at ON users;")
    op.execute("DROP INDEX IF EXISTS idx_users_verified;")
    op.execute("DROP INDEX IF EXISTS idx_users_active;")
    op.execute("DROP INDEX IF EXISTS idx_users_email;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
    op.execute("DROP TYPE IF EXISTS oauth_provider CASCADE;")
    op.execute("DROP TABLE IF EXISTS role_permissions CASCADE;")
    op.execute("DROP TABLE IF EXISTS permissions CASCADE;")
    op.execute("DROP TABLE IF EXISTS roles CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS fn_set_updated_at;")
