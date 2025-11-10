# Modern FastAPI Project with Complete Toolchain

This is a FastAPI project configured with a modern development toolchain. It uses `pyproject.toml` as the single source of truth (according to PEP 621) for dependency management and tool configuration, ensuring consistency, reproducibility, and code quality best practices.

## Core Specifications and Technologies

The philosophy of this project is centralization and automation.

  * **Framework:** `FastAPI`
  * **ASGI Server:** `Uvicorn` (for development and as a production worker)
  * **WSGI/Process Manager Server:** `Gunicorn` (for managing workers in production)
  * **Central Configuration:** `pyproject.toml` (manages dependencies and configurations for all tools)
  * **Linter & Formatter:** `Ruff` (replacing Black, Flake8, and isort)
  * **Security:** `Bandit` (vulnerability scanner)
  * **Type Checking:** `MyPy` (static type checker)
  * **Testing:** `Pytest` (with `pytest-cov` for coverage)
  * **App Configuration:** `Pydantic-Settings` (environment variables and secrets management)
  * **Task Automation:** `Makefile` (portable orchestrator for common tasks like `lint`, `test`, `run`)
  * **Git Hooks:** `pre-commit` (ensures code quality before each commit)

---

## Project Structure

The project follows a **Domain-Driven Design (DDD)** and **Clean Architecture–inspired** structure, promoting scalability, maintainability, and clear separation of concerns.

```
.
├── app/                       # Main application package
│   ├── __init__.py
│   ├── main.py                # FastAPI entry point (app initialization)
│   │
│   ├── api/                   # API layer (controllers / routes)
│   │   ├── v1/                # Versioned API endpoints
│   │   │   ├── users.py
│   │   │   ├── movies.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── core/                  # Core configurations and utilities
│   │   ├── config.py          # Application settings (Pydantic Settings)
│   │   ├── security.py        # Authentication and authorization
│   │   ├── logging.py         # Logging configuration
│   │   └── __init__.py
│   │
│   ├── domains/               # Domain layer (business logic and entities)
│   │   ├── users/
│   │   │   ├── models.py      # SQLAlchemy ORM models
│   │   │   ├── schemas.py     # Pydantic schemas
│   │   │   ├── repository.py  # Database operations
│   │   │   ├── services.py    # Business logic / use cases
│   │   │   └── __init__.py
│   │   ├── movies/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── services.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── db/                    # Database infrastructure layer
│   │   ├── session.py         # Async session and engine management
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   ├── migrations/        # Alembic migrations
│   │   └── __init__.py
│   │
│   └── dependencies.py        # Shared dependency injection definitions
│
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_main.py
│
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── Makefile                   # Common development commands
└── pyproject.toml             # Project dependencies and build configuration
```

-----

## 1\. Development Environment

### 1.1. Prerequisites

  * **Python 3.12+** installed on the system
  * **Git** installed
  * **Make** (optional, but recommended for automation)

### 1.2. Initial Setup

#### Option A: Using Makefile (Recommended - Linux/macOS/Windows with Make)

**1. Clone the repository:**

```bash
git clone <your-repository-url>
cd <project-name>
```

**2. Set up the environment and install dependencies:**

```bash
make install-dev
```

This command will automatically:

  * Create a local virtual environment at `./.venv/`
  * Install the `app/` package in editable mode
  * Install all production and development dependencies

**3. Install Git Hooks:**

```bash
.venv/bin/pre-commit install
```

#### Option B: Without Makefile (All Operating Systems)

##### Linux / macOS

**1. Clone the repository:**

```bash
git clone <your-repository-url>
cd <project-name>
```

**2. Create the virtual environment:**

```bash
python3 -m venv .venv
```

**3. Activate the virtual environment:**

```bash
source .venv/bin/activate
```

**4. Update pip:**

```bash
pip install --upgrade pip
```

**5. Install dependencies:**

```bash
pip install -e ".[dev]"
```

**6. Install pre-commit hooks:**

```bash
pre-commit install
```

##### Windows (PowerShell)

**1. Clone the repository:**

```powershell
git clone <your-repository-url>
cd <project-name>
```

**2. Create the virtual environment:**

```powershell
python -m venv .venv
```

**3. Activate the virtual environment:**

```powershell
.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. Update pip:**

```powershell
python -m pip install --upgrade pip
```

**5. Install dependencies:**

```powershell
pip install -e ".[dev]"
```

**6. Install pre-commit hooks:**

```powershell
pre-commit install
```

##### Windows (CMD)

**1. Clone the repository:**

```cmd
git clone <your-repository-url>
cd <project-name>
```

**2. Create the virtual environment:**

```cmd
python -m venv .venv
```

**3. Activate the virtual environment:**

```cmd
.venv\Scripts\activate.bat
```

**4. Update pip:**

```cmd
python -m pip install --upgrade pip
```

**5. Install dependencies:**

```cmd
pip install -e ".[dev]"
```

**6. Install pre-commit hooks:**

```cmd
pre-commit install
```

### 1.3. Running the Application

#### With Makefile:

```bash
make run
```

#### Without Makefile:

##### Linux / macOS:

```bash
source .venv/bin/activate
python -m uvicorn app.main:create_app --factory --reload
```

##### Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:create_app --factory --reload
```

##### Windows (CMD):

```cmd
.venv\Scripts\activate.bat
python -m uvicorn app.main:create_app --factory --reload
```

The application will be available at:

  * **API:** `http://127.0.0.1:8000`
  * **Documentation (Swagger):** `http://127.0.0.1:8000/docs`
  * **Documentation (ReDoc):** `http://127.0.0.1:8000/redoc`

-----

## 2\. Development Workflow

### 2.1. Toolchain Commands

#### With Makefile:

| Command          | Description                                 |
| ---------------- | ------------------------------------------- |
| `make lint`      | Runs Ruff linter and Bandit scanner         |
| `make format`    | Formats code with Ruff                      |
| `make typecheck` | Checks types with MyPy                      |
| `make test`      | Runs tests with Pytest and shows coverage   |
| `make run`       | Starts the development server               |
| `make clean`     | Removes virtual environment and cache files |
| `make help`      | Shows all available commands                |

#### Without Makefile:

##### Linux / macOS (with environment activated):

```bash
# Linting
python -m ruff check app/ tests/
python -m bandit -c pyproject.toml -r app/

# Formatting
python -m ruff format app/ tests/

# Type checking
python -m mypy --config-file=pyproject.toml app/

# Tests
python -m pytest --cov=app --cov-report=term-missing

# Run application
python -m uvicorn app.main:create_app --factory --reload
```

##### Windows (with environment activated):

```powershell
# Linting
python -m ruff check app/ tests/
python -m bandit -c pyproject.toml -r app/

# Formatting
python -m ruff format app/ tests/

# Type checking
python -m mypy --config-file=pyproject.toml app/

# Tests
python -m pytest --cov=app --cov-report=term-missing

# Run application
python -m uvicorn app.main:create_app --factory --reload
```

### 2.2. Checklist Before Committing

**IMPORTANT:** Always run these commands before committing your changes:

#### Manual Process (Step-by-Step):

##### 1\. Activate the virtual environment (if not active):

**Linux/macOS:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
.venv\Scripts\activate.bat
```

##### 2\. Format the code:

```bash
python -m ruff format app/ tests/
```

##### 3\. Fix linting problems automatically:

```bash
python -m ruff check --fix app/ tests/
```

##### 4\. Check linting (without auto-fix):

```bash
python -m ruff check app/ tests/
```

If there are errors, fix them manually before continuing.

##### 5\. Run security scanner:

```bash
python -m bandit -c pyproject.toml -r app/
```

If there are vulnerabilities, fix them before continuing.

##### 6\. Check static types:

```bash
python -m mypy --config-file=pyproject.toml app/
```

Fix any typing errors before continuing.

##### 7\. Run tests:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Ensure all tests pass and coverage is adequate.

##### 8\. Add your changes to Git:

```bash
git add .
```

##### 9\. Commit:

```bash
git commit -m "Your commit message"
```

**Note:** If you installed pre-commit (`pre-commit install`), steps 2-6 will be executed automatically when you try to commit. If any check fails, the commit will be blocked until you fix the problems.

#### Using Pre-commit Hooks (Automatic):

If you installed the pre-commit hooks, simply:

```bash
git add .
git commit -m "Your commit message"
```

Pre-commit will automatically run:

  * Ruff format
  * Ruff check (with --fix)
  * MyPy
  * Bandit
  * Checks for whitespace, YAML, TOML

If any check fails, fix the problems and try to commit again.

#### Quick Command (With Makefile):

```bash
make format && make lint && make typecheck && make test
```

If all commands pass successfully, you are ready to commit\!

### 2.3. Running Pre-commit Manually

To run all pre-commit checks without committing:

```bash
pre-commit run --all-files
```

-----

## 3\. Production Environment

### 3.1. Key Differences (Dev vs. Prod)

1.  **Dependencies:** Install **only** production dependencies (without `[dev]`)
2.  **Server:** Use `gunicorn` with multiple workers, never `--reload`
3.  **Configuration:** Use environment variables, never `.env` files
4.  **Logging:** Configure structured JSON logs
5.  **Debug:** Always disable `debug=True` in FastAPI

### 3.2. Production Installation

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Install ONLY production dependencies
pip install -e .
```

### 3.3. Production Run Command

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app \
  --workers 4 \
  --bind 0.0.0.0:80
```

Adjust `--workers` based on the server's CPU: `(2 * CPU_CORES) + 1`

### 3.4. Example Dockerfile

```dockerfile
# --- Stage 1: Builder ---
FROM python:3.12-slim as builder

WORKDIR /app
RUN pip install --upgrade pip

COPY pyproject.toml .
RUN pip install --prefix=/install .

# --- Stage 2: Final ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY ./app /app/app

EXPOSE 80

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
     "app.main:app", "--workers", "4", "--bind", "0.0.0.0:80"]
```

-----

## 4\. Configuration Management

### 4.1. Development

1.  Copy the example file:

    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` with your local settings:

    ```
    DATABASE_URL=postgresql://user:pass@localhost/db
    SECRET_KEY=your-secret-key-here
    DEBUG=True
    ```

3.  **IMPORTANT:** Never commit the `.env` file (it must be in `.gitignore`)

### 4.2. Production

Define environment variables directly in the system:

**Linux/macOS:**

```bash
export DATABASE_URL="postgresql://user:pass@prod-host/db"
export SECRET_KEY="production-secret-key"
export DEBUG="False"
```

**Windows PowerShell:**

```powershell
$env:DATABASE_URL="postgresql://user:pass@prod-host/db"
$env:SECRET_KEY="production-secret-key"
$env:DEBUG="False"
```

**Docker/Kubernetes:**
Use secrets management and environment variables in the container configuration.

-----

## 5\. Troubleshooting

### Problem: "Module not found" when running the application

**Solution:** Ensure the virtual environment is activated and the project was installed in editable mode:

```bash
pip install -e ".[dev]"
```

### Problem: Pre-commit doesn't work on Windows

**Solution:** Run PowerShell as administrator and adjust the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Permission error on Linux/macOS

**Solution:** Do not use `sudo` with pip. Use virtual environments to isolate dependencies.

### Problem: Tests failing locally

**Solution:** Ensure all development dependencies are installed:

```bash
pip install -e ".[dev]"
```

-----

## 6\. Additional Resources

  * **FastAPI Documentation:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
  * **Ruff Documentation:** [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)
  * **Pydantic Documentation:** [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
  * **Pytest Documentation:** [https://docs.pytest.org/](https://docs.pytest.org/)

-----

## 7\. Contributing

1.  Fork the project
2.  Create a branch for your feature (`git checkout -b feature/new-feature`)
3.  Follow the checklist before committing (section 2.2)
4.  Commit your changes (`git commit -m 'Adds new feature'`)
5.  Push to the branch (`git push origin feature/new-feature`)
6.  Open a Pull Request

-----

## License

[Specify the project license here]
