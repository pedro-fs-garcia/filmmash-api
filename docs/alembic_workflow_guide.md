# 🧭 Alembic Workflow Guide — Database Migrations

This document explains how to manage the database schema using **Alembic**.
All developers should follow these instructions when changing models or deploying to production.

---

## 📘 1. Overview — What is Alembic?

Alembic is a **database migration tool** that works together with **SQLAlchemy**.
It keeps the database structure (tables, columns, relationships) synchronized with your Python models.

Think of Alembic like **Git for your database schema**:

| Git concept | Alembic equivalent |
| ----------- | ------------------ |
| Repository  | Database schema    |
| Commit      | Migration revision |
| Push        | Upgrade database   |
| Revert      | Downgrade database |

---

## 🧩 2. Folder Structure

When you initialize Alembic (`alembic init alembic`), it creates this structure:

```
alembic/
│
├── versions/          # Each migration (like a Git commit)
│   ├── xxxx_initial.py
│   └── yyyy_add_movies_table.py
│
├── env.py             # Alembic configuration (don’t edit often)
└── alembic.ini        # Global Alembic settings
```

👉 **All of this folder (including `versions/`) must be committed to Git.**

Each migration file describes how to **upgrade** or **downgrade** the schema.

---

## 💻 3. Local Development

During development, we want to:

* Automatically create the database if it doesn’t exist.
* Use Alembic to create and apply schema migrations when models change.

### 🧱 Step 1: Make sure the database exists

If you just cloned the project, the app should **automatically create** the database on startup in development mode (check your backend’s `init_postgres_db()` or equivalent function).

If not, create it manually:

```bash
createdb <your_database_name>
```

---

### ✏️ Step 2: Make changes to your SQLAlchemy models

Edit or create new models in `app/db/postgres/models.py` or similar.

For example:

```python
class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
```

---

### 🏗 Step 3: Generate a migration

Each time you modify the models (add a table, change a column, etc.), generate a new migration:

```bash
alembic revision --autogenerate -m "describe your change here"
```

Examples:

```bash
alembic revision --autogenerate -m "create movies table"
alembic revision --autogenerate -m "add release_date column to movies"
```

Alembic compares:

* The models in your code (`Base.metadata`)
* The actual database schema

and generates a migration file under `alembic/versions/`.

---

### 🔍 Step 4: Review the generated migration file

Before applying it, **always open the generated file** inside `alembic/versions/` and verify:

* The changes make sense (no accidental table drops!)
* The `upgrade()` and `downgrade()` sections are correct

If it looks good, proceed.

---

### 🚀 Step 5: Apply migrations to your local database

Run:

```bash
alembic upgrade head
```

This applies all new migrations and updates your local schema to the latest version.

If you need to roll back one version:

```bash
alembic downgrade -1
```

---

### ✅ Step 6: Commit your migration

Always commit both your **code changes** and **migration file** together:

```bash
git add .
git commit -m "Add movies table migration"
```

This keeps the database and models in sync across all environments.

---

## 🏭 4. Production Environment

In production, the database already exists and should **never be auto-created** by the application.

Instead, we use Alembic to keep it updated safely.

### 📦 Step 1: Deploy your code

Deploy the new version of your backend (which includes the new models and migration files).

---

### ⚙️ Step 2: Apply migrations in production

On the production server, after deploying:

```bash
alembic upgrade head
```

This will:

* Run any new migrations that were not applied yet.
* Create or alter tables as needed.

---

### 🚫 Step 3: Never autogenerate directly in production

**Never** run `alembic revision --autogenerate` in production.
That command should only be used by developers in local development.

Production should only use:

```bash
alembic upgrade head
```

---

## 🧰 5. Common Commands Reference

| Command                                        | Description                                 |
| ---------------------------------------------- | ------------------------------------------- |
| `alembic revision --autogenerate -m "message"` | Generate new migration file                 |
| `alembic upgrade head`                         | Apply all migrations to the latest version  |
| `alembic downgrade -1`                         | Roll back one migration                     |
| `alembic history`                              | Show all migrations applied or pending      |
| `alembic current`                              | Show current schema version in the database |
| `alembic heads`                                | Show latest revision(s) available           |

---

## 🧼 6. Troubleshooting

### ❌ “Target database is not up to date”

Run:

```bash
alembic upgrade head
```

Then try generating the revision again.

---

### ❌ Database doesn’t exist

In development, the app should create it automatically.
If not, create it manually or ensure your `init_postgres_db()` runs on startup.

---

### ❌ Empty autogenerate

If `--autogenerate` creates an empty migration, make sure:

* The models import correctly.
* `Base.metadata` is properly defined and included in `target_metadata` in `env.py`.

---

## 🧭 7. Summary — Developer Workflow

1. Modify or create SQLAlchemy models
2. Run: `alembic revision --autogenerate -m "your message"`
3. Review the generated file
4. Apply it: `alembic upgrade head`
5. Commit both the model and migration
6. Push to repository
7. In production: only run `alembic upgrade head`
