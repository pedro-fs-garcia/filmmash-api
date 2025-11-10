# run:
# 	uvicorn app.main:create_app --factory --reload

# lint:
# 	ruff check app/
# 	bandit -r app/

# format:
# 	ruff format app/

# typecheck:
# 	mypy app/

# test:
# 	pytest --cov=app --cov-report=term-missing

.PHONY: all install-dev lint format typecheck test run clean help

VENV =.venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

all: install-dev

$(PYTHON): pyproject.toml
	@echo "Creating virtual environment at $(VENV)..."
	python3 -m venv $(VENV)
	@echo "Updating pip..."
	$(PIP) install --upgrade pip
	@echo "Virtual Environment is ready."

install-dev: $(PYTHON)
	@echo "Installing project dependencies (with 'dev' extras)..."
	# Instala o projeto (app/) em modo editável (-e) e
	# as dependências opcionais [dev] do pyproject.toml.
	$(PIP) install -e ".[dev]"
	@echo "Dependencies installed."

lint: install-dev
	@echo "Running Ruff linter..."
	$(PYTHON) -m ruff check app/ tests/
	@echo "Running Bandit scanner..."
	# Usa a configuração centralizada no pyproject.toml [5, 6]
	$(PYTHON) -m bandit -c pyproject.toml -r app/

format: install-dev
	@echo "Formatting code with Ruff..."
	$(PYTHON) -m ruff format app/ tests/

typecheck: install-dev
	@echo "Running MyPy..."
	$(PYTHON) -m mypy --config-file=pyproject.toml app/

test: install-dev
	@echo "Running tests..."
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

run: install-dev
	@echo "Starting FastAPI server at http://127.0.0.1:8000"
	$(PYTHON) -m uvicorn app.main:create_app --factory --reload

clean:
	@echo "Cleaning environment and cache files..."
	rm -rf $(VENV).mypy_cache.pytest_cache.ruff_cache/
	find. -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleanup completed."

help:
	@grep -E '^[a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
