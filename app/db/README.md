# db/ Module

Database layer for the application, currently providing async PostgreSQL support via SQLAlchemy.

## Structure

```
db/
├── __init__.py          # Public API: PgSessionDep, init_postgres_db, close_postgres_db
├── exceptions.py        # Shared database exceptions
├── mongo/               # Reserved for future MongoDB support
└── postgres/
    ├── base.py          # SQLAlchemy DeclarativeBase for all models
    ├── dependencies.py  # FastAPI session dependency
    ├── engine.py        # Engine and session factory configuration
    └── init_db.py       # Database initialization and teardown
```

## Public API

Everything needed by external modules is re-exported from `app.db`:

```python
from app.db import init_postgres_db, close_postgres_db, PgSessionDep
```

| Symbol              | Type                      | Description                                                  |
| ------------------- | ------------------------- | ------------------------------------------------------------ |
| `init_postgres_db`  | `async () -> None`        | Creates the database if it doesn't exist, then creates all tables. |
| `close_postgres_db` | `async () -> None`        | Disposes of the engine connection pool.                      |
| `PgSessionDep`      | FastAPI `Annotated` type  | Inject an `AsyncSession` into route handlers via `Depends`.  |

## Configuration

The engine reads connection settings from `app.core.config.get_settings()`. The relevant environment variables are:

| Variable            | Default        |
| ------------------- | -------------- |
| `POSTGRES_USER`     | `postgres`     |
| `POSTGRES_PASSWORD` | `postgres`     |
| `POSTGRES_HOST`     | `localhost`    |
| `POSTGRES_PORT`     | `5432`         |
| `POSTGRES_DB`       | `filmmash_db`  |

These are composed into an `asyncpg` connection URL:

```
postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}
```

## Lifecycle

### Startup — `init_postgres_db()`

Called during the FastAPI lifespan (in development mode). It:

1. Connects to the default `postgres` database with `AUTOCOMMIT` isolation.
2. Checks `pg_database` for the target database name. If it's missing, creates it.
3. Connects to the target database and recreates all tables (`drop_all` + `create_all` from `Base.metadata`).
4. Retries the full process up to **10 times** (with 500 ms delay) if any connection error occurs.

> **Warning:** `init_postgres_db` drops and recreates all tables on every call. It is intended for development only. In production, use Alembic migrations.

### Shutdown — `close_postgres_db()`

Called when the application shuts down. Disposes the async engine, releasing all pooled connections.

## Session Management

### Engine (`engine.py`)

A single `AsyncEngine` is created at module load with:

- `echo=True` — logs all SQL statements.
- `future=True` — enables SQLAlchemy 2.0 style.

The `async_session` factory produces sessions configured with:

- `autocommit=False`
- `autoflush=False`
- `expire_on_commit=False`

### Dependency (`dependencies.py`)

`get_postgres_session()` is an async generator that yields one `AsyncSession` per request and closes it at the end:

```python
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db_session:
        yield db_session
```

Use `PgSessionDep` as a type annotation in FastAPI route parameters to inject a session automatically:

```python
from app.db import PgSessionDep

@router.get("/items")
async def list_items(db: PgSessionDep):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

For tests, override the dependency to use a test database session:

```python
from app.db.postgres.dependencies import get_postgres_session

app.dependency_overrides[get_postgres_session] = my_test_session_generator
```

## Defining Models

All SQLAlchemy models must inherit from `Base`:

```python
from app.db.postgres.base import Base
from sqlalchemy import Column, String

class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True)
```

## Database Exceptions

`db.exceptions` provides two reusable exceptions for repository layers:

| Exception                   | Attributes                    | Message format                                             |
| --------------------------- | ----------------------------- | ---------------------------------------------------------- |
| `ResourceAlreadyExistsError`| `resource_name`, `identifier` | `"{resource_name} with identifier {identifier} already exists"` |
| `ResourceNotFoundError`     | `resource_name`, `identifier` | `"{resource_name} with identifier {identifier} does not exists"` |

Usage:

```python
from app.db.exceptions import ResourceNotFoundError

raise ResourceNotFoundError("User", user_id)
```
