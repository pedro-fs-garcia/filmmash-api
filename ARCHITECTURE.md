# Project Architecture

This document outlines the architecture and project structure guidelines for this FastAPI project. It is designed to ensure maintainability, scalability, and clarity throughout the development process.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Decisions](#architecture-decisions)
3. [Project Structure](#project-structure)
4. [Layer Responsibilities](#layer-responsibilities)
5. [Data Flow](#data-flow)
6. [Requirements](#requirements)
7. [Development Tools](#development-tools)
8. [Getting Started](#getting-started)

---

## Overview

This project follows a **hybrid architecture** combining:

- **FastAPI official patterns** for the web layer
- **Domain-Driven Design (DDD) lite** for business logic organization
- **Clean Architecture principles** for dependency management

### Why This Structure?

| Approach                   | Pros                         | Cons                              | Our Choice |
| -------------------------- | ---------------------------- | --------------------------------- | ---------- |
| FastAPI Official (by type) | Simple, documented           | High coupling, hard to scale      | ❌          |
| Full DDD                   | Decoupled, scalable          | Overengineered for small projects | ❌          |
| **Hybrid (by domain)**     | Balanced, scalable, cohesive | Slightly more initial setup       | ✅          |

---

## Architecture Decisions

### ADR-001: Domain-Centric Structure

**Context:** We need a structure that scales from MVP to enterprise.

**Decision:** Organize code by business domain (`domains/`) rather than by technical layer (`routers/`, `models/`).

**Consequences:**
- ✅ Each domain is self-contained and can be developed independently
- ✅ Easy to delete or extract a domain
- ✅ Reduces merge conflicts in large teams
- ⚠️ Slightly more files per feature

### ADR-002: Separate Entity from ORM Model

**Context:** Domain logic should not depend on persistence details.

**Decision:** Use `entities.py` for pure domain logic and `models.py` for SQLAlchemy ORM.

**Consequences:**
- ✅ Domain logic is testable without database
- ✅ Can switch ORM without changing business rules
- ⚠️ Requires mapping between entity and model

### ADR-003: Repository Pattern

**Context:** We need to abstract database operations for testability.

**Decision:** Use repository classes that translate between entities and models.

**Consequences:**
- ✅ Easy to mock for unit tests
- ✅ Database logic centralized
- ⚠️ Additional abstraction layer

---

## Project Structure

```
/
├── alembic/                        # 🗃️ Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # Application factory
│   │
│   ├── core/                       # ⚙️ Shared Kernel & Configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Environment settings (Pydantic)
│   │   ├── logger.py               # Structured logging (JSON)
│   │   ├── security.py             # JWT, password hashing
│   │   ├── middleware.py           # CORS, request ID, timing
│   │   ├── exceptions.py           # Global exception handlers
│   │   ├── response.py             # Standardized API responses
│   │   └── shared/                 # Base classes for DDD
│   │       ├── __init__.py
│   │       ├── entity.py           # Base Entity, AggregateRoot
│   │       ├── value_object.py     # Base ValueObject
│   │       └── repository.py       # Repository Protocol
│   │
│   ├── domains/                    # 🧠 Business Domains (Bounded Contexts)
│   │   ├── __init__.py
│   │   │
│   │   ├── film/                   # Film domain
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # HTTP endpoints
│   │   │   ├── service.py          # Business logic orchestration
│   │   │   ├── repository.py       # Data access abstraction
│   │   │   ├── entities.py         # Domain entities (pure Python)
│   │   │   ├── models.py           # SQLAlchemy ORM models
│   │   │   ├── schemas.py          # Pydantic DTOs (request/response)
│   │   │   ├── exceptions.py       # Domain-specific exceptions
│   │   │   └── dependencies.py     # FastAPI dependency injection
│   │   │
│   │   ├── match/                  # Match domain
│   │   │   └── ... (same structure)
│   │   │
│   │   ├── user/                   # User domain
│   │   │   └── ...
│   │   │
│   │   └── auth/                   # Authentication domain
│   │       └── ...
│   │
│   ├── infrastructure/             # 🔌 External Services & Integrations
│   │   ├── __init__.py
│   │   ├── tmdb/                   # TMDB API client
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # HTTP client
│   │   │   └── schemas.py          # Response DTOs
│   │   ├── cache/                  # Caching layer
│   │   │   ├── __init__.py
│   │   │   └── redis.py            # Redis client
│   │   └── messaging/              # Event dispatching (future)
│   │       └── __init__.py
│   │
│   ├── api/                        # 🌐 API Composition & Versioning
│   │   ├── __init__.py
│   │   ├── v1.py                   # v1 router aggregation
│   │   └── health.py               # Health check endpoints
│   │
│   └── db/                         # 🗄️ Database Configuration
│       ├── __init__.py
│       ├── base.py                 # SQLAlchemy declarative base
│       ├── session.py              # Session factory & dependency
│       └── init_db.py              # Database initialization
│
├── docs/                           # 📚 Documentation
│   ├── adr/                        # Architecture Decision Records
│   └── api/                        # API documentation extras
│
├── logs/                           # 📝 Application logs
│
├── tests/                          # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/                       # Unit tests
│   │   ├── domains/
│   │   │   ├── film/
│   │   │   └── match/
│   │   └── core/
│   ├── integration/                # Integration tests
│   │   └── domains/
│   └── e2e/                        # End-to-end tests
│       └── api/
│
├── scripts/                        # 🔧 Utility scripts
│   ├── seed.py                     # Database seeding
│   └── migrate.py                  # Migration helpers
│
├── .env.example                    # Environment template
├── .pre-commit-config.yaml         # Pre-commit hooks
├── pyproject.toml                  # Project configuration
├── Makefile                        # Development commands
├── docker-compose.yml              # Local development stack
└── README.md                       # Project overview
```

---

## Layer Responsibilities

### Core Layer (`app/core/`)

**Purpose:** Shared utilities, configuration, and base classes.

| File            | Responsibility                             |
| --------------- | ------------------------------------------ |
| `config.py`     | Environment variables, settings validation |
| `logger.py`     | Structured JSON logging, async handlers    |
| `security.py`   | JWT encoding/decoding, password hashing    |
| `middleware.py` | CORS, request tracing, timing              |
| `exceptions.py` | Global exception handlers, error responses |
| `response.py`   | Standardized API response format           |
| `shared/`       | Base classes for entities, repositories    |

**Dependencies:** None (lowest level)

---

### Domains Layer (`app/domains/`)

**Purpose:** Business logic organized by bounded context.

Each domain contains:

| File              | Responsibility                    | Depends On                     |
| ----------------- | --------------------------------- | ------------------------------ |
| `router.py`       | HTTP endpoints, request handling  | `service.py`, `schemas.py`     |
| `service.py`      | Business logic orchestration      | `repository.py`, `entities.py` |
| `repository.py`   | Data access, entity-model mapping | `models.py`, `entities.py`     |
| `entities.py`     | Pure domain logic, business rules | `core/shared/`                 |
| `models.py`       | SQLAlchemy ORM definitions        | `db/base.py`                   |
| `schemas.py`      | Pydantic DTOs for API             | None                           |
| `exceptions.py`   | Domain-specific errors            | `core/exceptions.py`           |
| `dependencies.py` | FastAPI DI setup                  | `repository.py`, `service.py`  |

**Domain Interaction Rules:**
- ✅ Domains can import from `core/`
- ✅ Domains can import from `infrastructure/`
- ⚠️ Domains should minimize imports from other domains
- ❌ Domains must not import from `api/`

---

### Infrastructure Layer (`app/infrastructure/`)

**Purpose:** External service integrations.

| Component    | Responsibility                     |
| ------------ | ---------------------------------- |
| `tmdb/`      | TMDB API client for movie data     |
| `cache/`     | Redis caching operations           |
| `messaging/` | Event bus, message queues (future) |

**Dependencies:** `core/` only

---

### API Layer (`app/api/`)

**Purpose:** API versioning and router aggregation.

| File        | Responsibility                       |
| ----------- | ------------------------------------ |
| `v1.py`     | Aggregates all domain routers for v1 |
| `health.py` | Health check, readiness, liveness    |

**Dependencies:** `domains/*/router.py`

---

### Database Layer (`app/db/`)

**Purpose:** Database connection and session management.

| File         | Responsibility                                  |
| ------------ | ----------------------------------------------- |
| `base.py`    | SQLAlchemy declarative base                     |
| `session.py` | Async session factory, `get_session` dependency |
| `init_db.py` | Database creation, table initialization         |

**Dependencies:** `core/config.py`

---

## Data Flow

### Request Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                          HTTP Request                            │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                         Middleware                               │
│              (CORS, Request ID, Logging, Timing)                 │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Router (router.py)                          │
│         - Validates request (Pydantic schemas.py)                │
│         - Injects dependencies (dependencies.py)                 │
│         - Handles HTTP concerns                                  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Service (service.py)                         │
│         - Orchestrates business logic                            │
│         - Coordinates multiple repositories                      │
│         - Enforces business rules                                │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Repository (repository.py)                     │
│         - Maps Entity ↔ Model                                    │
│         - Executes database queries                              │
│         - Abstracts persistence                                  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Database (db/)                              │
│         - SQLAlchemy async session                               │
│         - PostgreSQL                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Dependency Direction

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│    api/     │────▶│  domains/   │────▶ │     core/       │
│  (routers)  │      │ (business)  │      │ (shared kernel) │
└─────────────┘      └──────┬──────┘      └─────────────────┘
                            │
                            ▼
                   ┌──────────────┐      ┌─────────────────┐
                   │infrastructure│────▶│      db/        │
                   │  (external)  │      │  (persistence)  │
                   └──────────────┘      └─────────────────┘
```

**Rule:** Dependencies point inward. Inner layers know nothing about outer layers.

---

## Requirements

### Functional Requirements

| ID    | Requirement                          | Domain                        |
| ----- | ------------------------------------ | ----------------------------- |
| FR-01 | Users can create an account          | `user`, `auth`                |
| FR-02 | Users can login and receive JWT      | `auth`                        |
| FR-03 | Users can view film pairs for voting | `film`, `match`               |
| FR-04 | Users can vote for a film in a match | `match`                       |
| FR-05 | System calculates ELO ratings        | `film`                        |
| FR-06 | Users can view film rankings         | `film`                        |
| FR-07 | Films are fetched from TMDB          | `film`, `infrastructure/tmdb` |

### Non-Functional Requirements

| ID     | Requirement                            | Target       |
| ------ | -------------------------------------- | ------------ |
| NFR-01 | Response time < 200ms (p95)            | Performance  |
| NFR-02 | Support 1000 concurrent users          | Scalability  |
| NFR-03 | 99.9% uptime                           | Availability |
| NFR-04 | Test coverage > 80%                    | Quality      |
| NFR-05 | Zero critical security vulnerabilities | Security     |

### Technical Requirements

| Category   | Technology | Version |
| ---------- | ---------- | ------- |
| Runtime    | Python     | 3.12+   |
| Framework  | FastAPI    | 0.110+  |
| ORM        | SQLAlchemy | 2.0+    |
| Database   | PostgreSQL | 15+     |
| Cache      | Redis      | 7+      |
| Migrations | Alembic    | 1.13+   |
| Validation | Pydantic   | 2.0+    |

---

## Development Tools

### Makefile Commands

```makefile
# Installation
make install          # Install all dependencies
make install-dev      # Install with dev dependencies

# Development
make run              # Start development server
make run-prod         # Start production server

# Database
make db-upgrade       # Run migrations
make db-downgrade     # Rollback last migration
make db-revision      # Create new migration
make db-reset         # Reset database

# Quality
make lint             # Run all linters
make format           # Format code
make type-check       # Run mypy
make security-check   # Run bandit

# Testing
make test             # Run all tests
make test-unit        # Run unit tests only
make test-cov         # Run tests with coverage

# Docker
make docker-up        # Start containers
make docker-down      # Stop containers
make docker-logs      # View logs
```

### Alembic (Migrations)

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

**Migration Naming Convention:** `YYYYMMDD_HHMM_description.py`

### Pre-commit Hooks

Configuration in `.pre-commit-config.yaml`:

| Hook             | Purpose                    |
| ---------------- | -------------------------- |
| `ruff`           | Linting and import sorting |
| `ruff-format`    | Code formatting            |
| `mypy`           | Type checking              |
| `bandit`         | Security scanning          |
| `detect-secrets` | Prevent secret commits     |

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Pytest

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific domain tests
pytest tests/unit/domains/film/

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

**Test file naming:** `test_*.py` or `*_test.py`

**Fixture locations:**
- `tests/conftest.py` — Shared fixtures
- `tests/unit/conftest.py` — Unit test fixtures
- `tests/integration/conftest.py` — Integration fixtures

### Formatting and Linting

```bash
# Lint code
ruff check app/

# Fix auto-fixable issues
ruff check app/ --fix

# Format code
ruff format app/

# Type checking
mypy app/

# Security scan
bandit -r app/
```

**Configuration:** All tools configured in `pyproject.toml`

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (optional)

### Local Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd filmmash-api

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install dependencies
make install-dev

# 4. Setup environment
cp .env.example .env
# Edit .env with your values

# 5. Start database
docker-compose up -d postgres

# 6. Run migrations
make db-upgrade

# 7. Start server
make run
```

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Metrics
curl http://localhost:8000/metrics
```

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
