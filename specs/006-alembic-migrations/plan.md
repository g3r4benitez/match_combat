# Implementation Plan: Alembic Migrations

**Branch**: `006-alembic-migrations` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-alembic-migrations/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Introduce Alembic as the database migration tool to replace the ad-hoc `SQLModel.metadata.create_all()` approach currently used in `init_db()`. This enables developers to evolve the database schema safely through version-controlled migration scripts, with support for autogenerate from model changes, sequential application, rollback, and fresh-database initialization. The integration targets SQLModel's `SQLModel.metadata` as the autogenerate source, with SQLite batch mode enabled for development and PostgreSQL native DDL for production.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.112.0, SQLModel 0.0.22, SQLAlchemy 2.0.15, Alembic 1.20.0 (new dependency)
**Storage**: PostgreSQL 16 (production via Docker Compose), SQLite (development, `sqlite:///./match_combat.db`)
**Testing**: pytest 8.3.2 with httpx
**Target Platform**: Linux server, Docker Compose for local services
**Project Type**: single (backend API - FastAPI)
**Performance Goals**: Migration script generation <30s (SC-001), fresh database initialization <1 min (SC-002), rollback to any previous version <30s (SC-004)
**Constraints**: Production database migrations reviewed and applied manually (not auto-applied); database configuration via environment variables in `app/core/config.py`; SQLite (development) requires Alembic batch mode for autogenerate due to limited ALTER TABLE support; existing manual SQL migration (`add_evento_area_columns.sql`) must be reconciled with new Alembic history; Dockerfile pins Python 3.9 (local dev is Python 3.11)
**Scale/Scope**: Single database serving a contact sport event management API; ~7 core tables (competidor, match, modalidad, evento, area, entrada, user) with modest cardinality per event; single-instance deployment (no horizontal scaling)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | No new API endpoints. Alembic is infrastructure/dev-tooling invoked via CLI (`alembic` commands), not HTTP. Existing `/api/<resource>/` conventions unchanged. Supports constitution requirement: "Database schema changes MUST be backward-compatible or accompanied by a migration strategy." |
| II. Domain Integrity | PASS | Migrations only evolve schema structure; matching criteria (sexo, edad, peso, historial, modalidad) are model-level, not affected by migration tooling. |
| III. Layered Architecture | PASS | Alembic config (`alembic/env.py`) imports `SQLModel.metadata` directly — this is migration tooling outside the Controller → Service → Repository → Model request-handling stack, not a layer skip. No application-layer code bypasses an adjacent layer. |
| IV. Data Consistency | PASS | Alembic enforces tracked, ordered, transactional schema changes. Foreign key constraints remain at database level. Directly supports "Database schema changes MUST be backward-compatible or accompanied by a migration strategy." |
| V. Simplicity and YAGNI | PASS | Alembic justified by explicit feature requirement. No speculative abstractions. Single new dependency. The transition from `create_all` to `alembic upgrade head` is a minimal, justified change. |

### Post-Design Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | No API endpoints added. Alembic is CLI/dev-tooling infrastructure. Contract documented in `contracts/migration-cli.md` (CLI command schema, not OpenAPI). |
| II. Domain Integrity | PASS | No matching domain changes. `matched`, `orden`, and FK integrity constraints are preserved through migrations. Data model documented in `data-model.md`. |
| III. Layered Architecture | PASS | `alembic/env.py` imports `SQLModel.metadata` directly — this is migration tooling, outside the Controller → Service → Repository → Model stack. No application-layer bypass. `app/core/database.py` change is minimal: `create_all` → `command.upgrade`. |
| IV. Data Consistency | PASS | Alembic enforces tracked, ordered, transactional schema changes with rollback capability. Foreign key constraints enforced at DB level via models. Naming convention (`app/models/__init__.py`) ensures deterministic FK names for SQLite batch safety. |
| V. Simplicity and YAGNI | PASS | One new dependency (Alembic 1.20.0). One config refinement (`DB_URL` honoring). One database.py change. Naming convention in `__init__.py` justified by SQLite batch mode requirement (R-006). No speculative abstractions. |

**Complexity Tracking post-design**: No violations. The naming convention addition to `app/models/__init__.py` is the only design expansion, and it is required for SQLite batch-mode correctness (research.md R-006), not speculative.

## Project Structure

### Documentation (this feature)

```text
specs/006-alembic-migrations/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Library and integration research
├── data-model.md        # Phase 1: Existing schema documentation
├── quickstart.md        # Phase 1: Quick implementation guide
├── contracts/           # Phase 1: Migration CLI contract
│   └── migration-cli.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
alembic/                       # NEW - Alembic environment directory
├── env.py                     # Database connection + SQLModel metadata config
├── script.py.mako             # Migration script template (default)
├── alembic.ini                # Alembic CLI configuration
└── versions/                  # Empty - migration scripts stored here

app/
├── core/
│   ├── config.py              # MODIFIED - Honor DB_URL env var directly
│   └── database.py            # MODIFIED - Replace create_all with alembic command runner
├── models/                    # All model definitions (source of truth for autogenerate)
│   ├── __init__.py            # MODIFIED - Add naming convention to SQLModel.metadata
│   ├── area.py
│   ├── competidor.py        # Includes Competidor, Match, Modalidad, Sexo
│   ├── entrada.py
│   ├── evento.py
│   ├── user.py              # Includes User, TokenBlacklist, PasswordResetToken
│   └── criterios.py         # DTO only (no table)
└── ...                        # Existing controllers, services, repositories unchanged

requirements.txt               # MODIFIED - Add alembic
Dockerfile                     # MODIFIED - Ensure alembic available at build time
docker-compose.yaml            # UNCHANGED
.env.example                   # UNCHANGED (DB_URL already present)
```

**Structure Decision**: Follows the existing single-backend-API project structure. All source lives under `app/` with layered subdirectories (`core/`, `models/`, `controllers/`, `services/`, `repositories/`). Alembic adds a top-level `alembic/` directory following the standard Alembic convention, with `versions/` holding autogenerated migration scripts. The only application-code change is in `app/core/database.py` where `create_all` is replaced by `alembic upgrade head`. No new application layers are introduced.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution gates pass without exceptions.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | - | - |
