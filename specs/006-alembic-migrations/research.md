# Research: Alembic Migrations

**Feature**: 006-alembic-migrations
**Date**: 2026-09-21
**Status**: All unknowns resolved

## R-001: Alembic Version Compatible with SQLAlchemy 2.0.15

**Decision**: Alembic 1.20.0 (latest available on PyPI)

**Rationale**: Alembic 1.20.0 is the current latest release. Alembic 1.12+ changed `compare_type` default to `True` and all 1.13+ releases maintain full SQLAlchemy 2.0 support. SQLAlchemy 2.0.15 is the version installed in this project. Alembic 1.20.0 is the most recent version that supports all features referenced in the documentation (batch mode, CHECK constraint detection v1.19+, naming conventions).

**Alternatives considered**:
- Alembic 1.13.3: Also supports SQLAlchemy 2.0 but lacks the newer CHECK constraint features and refinements. Rejected in favor of latest stable.
- Alembic 1.11.x and below: Predate SQLAlchemy 2.0 full support; not suitable.

## R-002: SQLModel + Alembic Autogenerate Integration Pattern

**Decision**: Use the standard `env.py` pattern with `target_metadata = SQLModel.metadata`, importing all model modules before setting metadata.

**Rationale**: SQLModel uses a single shared `MetaData` object (`SQLModel.metadata`) that all models registered with `table=True` write to. Alembic's autogenerate compares the reflected database schema against `target_metadata`. By importing all model modules in `env.py` before setting `target_metadata`, every table is registered and autogenerate can detect all tables, columns, constraints, and relationships.

**Key env.py configuration**:
```python
from sqlmodel import SQLModel
# Import ALL models so they register on SQLModel.metadata
from app.models.area import Area
from app.models.competidor import Competidor, Sexo, Modalidad, Match
from app.models.entrada import Entrada
from app.models.evento import Evento
from app.models.user import User, TokenBlacklist, PasswordResetToken

target_metadata = SQLModel.metadata

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,        # detect column type changes (default since 1.12, explicit for clarity)
    compare_server_default=True,  # detect server default changes (off by default)
    render_as_batch=(dialect_name == "sqlite"),  # batch mode for SQLite only
)
```

**Research sources**:
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Alembic Auto Generating Migrations: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

## R-003: SQLite Batch Mode Configuration

**Decision**: Conditionally enable `render_as_batch=True` only when `connection.dialect.name == "sqlite"`.

**Rationale**: SQLite has almost no ALTER TABLE support (only `add_column` and rename). Alembic's batch mode performs a "move and copy" workflow: CREATE temp table → INSERT data → DROP original → RENAME temp to original. The Alembic docs confirm this is "safe to use in all cases" because `batch_alter_table()` only activates the move-and-copy for SQLite; on PostgreSQL/MySQL it falls back to native ALTER. Gating on the dialect avoids any PostgreSQL edge cases with constraint naming during batch recreation.

**Key code pattern** (in `run_migrations_online()`):
```python
with connectable.connect() as connection:
    use_batch = connection.dialect.name == "sqlite"
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=use_batch,
    )
```

**Note on `alembic check`**: Works in batch mode because the reflection (schema comparison) logic is independent of how the ALTER is rendered. Autogenerate generates `with op.batch_alter_table(...)` directives automatically when batch mode is enabled.

**Research source**: Alembic Batch Mode docs: https://alembic.sqlalchemy.org/en/latest/batch.html

## R-004: Database URL Integration

**Decision**: Override `sqlalchemy.url` in `env.py` by reading `DB_URL` from `app.core.config`. Set `prepend_sys_path = .` in `alembic.ini` so the `app` package is importable.

**Rationale**: The application already constructs `DB_URL` in `app/core/config.py` from environment variables. The `.env` file defines `DB_URL="sqlite:///./match_combat.db"` for development and a PostgreSQL URL for production. However, `config.py` currently *ignores* the `DB_URL` env var and always builds a PostgreSQL URL from the broken-out vars. The recommended fix is to honor the explicit env var:

```python
# In config.py — honor DB_URL from .env, fall back to constructed URL
DB_URL: str = _config("DB_URL", cast=str, default=get_database_url())
```

This ensures both the application and Alembic use the same database URL source of truth. The `alembic.ini` should contain a placeholder `sqlalchemy.url` since the real value comes from `env.py`.

**Note**: `app/core/config.py:28` currently does `DB_URL: str = get_database_url()`, which always returns a PostgreSQL URL. The `.env` sets `DB_URL="sqlite:///./match_combat.db"` but it's not read. This needs fixing so Alembic and the app share the same URL.

## R-005: Initial Migration and `create_all` Replacement Strategy

**Decision**: 
1. Generate the initial migration via `alembic revision --autogenerate -m "initial schema"` against a clean database.
2. For the existing dev database (`match_combat.db` with tables already created by `create_all`): use `alembic stamp head` to adopt it without re-creating tables.
3. For fresh databases (CI, new environments): delete the DB file, then `alembic upgrade head`.
4. Replace `SQLModel.metadata.create_all(engine)` in `init_db()` (`app/core/database.py:16`) with `alembic upgrade head`.

**Rationale**: The existing manual SQL files (`add_evento_area_columns.sql`) and `create_all` have produced tables matching the current model definitions. The initial autogenerate migration will exactly mirror these models. The `stamp head` command marks the current revision in the `alembic_version` table without running DDL — ideal for existing databases where `create_all` already created the schema.

For `init_db()`, replacing `create_all` with `alembic upgrade head` means the app self-initializes at startup (already called from `main.py` lifespan). New environments start empty → `upgrade head` creates the full schema. Existing environments → already at head → no-op.

```python
# In database.py init_db()
from pathlib import Path
from alembic.config import Config
from alembic import command

def init_db():
    alembic_cfg = Config(str(Path(__file__).resolve().parent.parent.parent / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
```

## R-006: Naming Convention for Constraint Handling

**Decision**: Attach a `naming_convention` to `SQLModel.metadata` before models are defined, set in `app/models/__init__.py` (currently empty).

**Rationale**: SQLModel's `Field(foreign_key="evento.id")` produces *unnamed* foreign key constraints. On SQLite in batch mode, Alembic's "move and copy" workflow reflects existing constraints by name; unnamed constraints cannot be targeted for drop/modify operations. A naming convention assigns deterministic names to all constraints, which is critical for SQLite batch operations to work correctly on schema changes involving foreign keys (e.g., column drops, type changes).

```python
# In app/models/__init__.py (executed before any model import)
from sqlalchemy.schema import MetaData
from sqlmodel import SQLModel

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
SQLModel.metadata = MetaData(naming_convention=convention)
```

**Warning**: This must be set *before* any model class is defined (i.e., at the top of `app/models/__init__.py` and imported first in `env.py`).

## R-007: Known Gotchas

**Decision**: Document and mitigate all known issues. None are blockers.

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| `match` is a SQL keyword; `Match` model maps to table `match` | Potential quoting issues in hand-edited migrations | SQLAlchemy/SQLModel quotes the identifier automatically; be cautious when editing migration scripts manually |
| `Field(foreign_key=...)` in SQLModel creates unnamed FKs | SQLite batch mode can't reflect/drop unnamed constraints | Apply naming convention (R-006) |
| `echo=True` in `create_engine` in `database.py:12` | Verbose SQL logging to console in dev | No change needed; Alembic env.py uses separate engine |
| `CriteriosDTO` in `app/models/criterios.py` is not a table model | Should NOT be imported in env.py for autogenerate | Exclude from model imports; it has no `table=True` |
| Percent-encoding in DB URLs with special chars | URL parsing issues | No special chars in current URLs; document if needed |
| Python version mismatch (Dockerfile uses 3.9, dev uses 3.11) | Alembic 1.20 requires Python 3.8+; Dockerfile should be updated | Note for implementation; Alembic itself works on 3.9+ |

## Research Sources

1. Alembic 1.20.0 Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
2. Alembic Auto Generating Migrations: https://alembic.sqlalchemy.org/en/latest/autogenerate.html
3. Alembic Batch Mode (SQLite): https://alembic.sqlalchemy.org/en/latest/batch.html
4. Alembic on PyPI (versions, 1.20.0 latest): verified via `pip index versions alembic`
5. SQLAlchemy 2.0 + Alembic compatibility: confirmed via docs and pip availability

## CLI Command Reference (Consolidated)

```bash
# Project root has alembic.ini; run from there

# Development workflow
alembic revision --autogenerate -m "add field x to Y"   # generate migration
alembic upgrade head                                    # apply all pending
alembic upgrade +1                                      # apply one
alembic downgrade -1                                    # rollback one
alembic downgrade <rev>                                 # rollback to revision
alembic stamp head                                      # adopt existing DB (no DDL)
alembic stamp base                                      # reset version tracking
alembic current                                         # show current revision
alembic history                                         # show migration history
alembic branches                                        # show branch points
alembic merge -m "merge" <rev1> <rev2>                  # merge branches
alembic check                                           # CI gate: exit 1 if drift

# SQL-only / offline
alembic upgrade head -x sql               # or: alembic revision --autogenerate --sql
```
