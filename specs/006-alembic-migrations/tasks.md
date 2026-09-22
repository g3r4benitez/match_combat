# Tasks: Alembic Migrations

**Input**: Design documents from `/specs/006-alembic-migrations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/migration-cli.md, quickstart.md

**Tests**: No automated test tasks included. The feature specification defines "Independent Test" sections per user story — these are operational verification procedures (running alembic CLI commands and checking DB state), documented in quickstart.md and executed as tasks within each story phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `app/`, `alembic/`, `specs/006-alembic-migrations/` at repository root (existing project structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install Alembic dependency and initialize the migration environment

- [x] T001 Add `alembic>=1.20.0` to `requirements.txt` and install in virtual environment
  - Add the line `alembic>=1.20.0` to `requirements.txt`
  - Run `pip install alembic>=1.20.0` in the project's virtual environment (`.venv`)
  - Verify with `alembic --version` (expected output: `Alembic 1.20.0` or higher)

- [x] T002 Create `alembic/` environment directory via `alembic init alembic`
  - Run `alembic init alembic` from the project root
  - This creates: `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/README`, `alembic/versions/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure the Alembic environment so it correctly reads SQLModel metadata, handles SQLite batch mode, and integrates with the app's database configuration.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Configure `alembic.ini` for the match_combat project
  - Edit `alembic.ini` to set `prepend_sys_path = .` (so `app` package is importable)
  - Set `sqlalchemy.url = sqlite:///placeholder` (real URL read from `env.py` at runtime)
  - Keep default `script_location = %(here)s/alembic`

- [x] T004 [P] Create `alembic/env.py` with SQLModel metadata wiring and SQLite batch mode
  - Import `SQLModel` from `sqlmodel` and set `target_metadata = SQLModel.metadata`
  - Import ALL model modules (`app.models.area`, `app.models.competidor`, `app.models.entrada`, `app.models.evento`, `app.models.user`) so models register on `SQLModel.metadata`
  - Import `DB_URL` from `app.core.config` and use it as the database URL
  - In `run_migrations_online()`: set `compare_type=True` and `render_as_batch=True` only when `connection.dialect.name == "sqlite"`
  - In `run_migrations_offline()`: set `url=get_url()`, `literal_binds=True`, `compare_type=True`

- [x] T005 [P] Add naming convention to `app/models/__init__.py`
  - Currently empty (0 lines). Add a `naming_convention` dict for FK, PK, IX, UQ, CK constraints
  - Set `SQLModel.metadata = MetaData(naming_convention=convention)` **before** any model is imported anywhere
  - Import all model modules in `__init__.py` so the package is self-contained
  - This is REQUIRED for SQLite batch mode to handle unnamed foreign keys (research.md R-006)

- [x] T006 [P] Fix `app/core/config.py` to honor `DB_URL` env var
  - Currently `DB_URL: str = get_database_url()` always builds a PostgreSQL URL, ignoring the `.env` `DB_URL` setting
  - Change to: `DB_URL: str = _config("DB_URL", cast=str, default=get_database_url())`
  - This ensures dev (SQLite) and production (PostgreSQL) share one URL source of truth with Alembic

- [x] T007 Replace `SQLModel.metadata.create_all(engine)` with Alembic upgrade in `app/core/database.py`
  - In `init_db()` (`app/core/database.py:16`), replace `SQLModel.metadata.create_all(engine)` with:
    ```python
    from pathlib import Path
    from alembic.config import Config
    from alembic import command
    def init_db():
        alembic_cfg = Config(str(Path(__file__).resolve().parent.parent.parent / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
    ```
  - The app startup in `app/main.py` already calls `init_db()` at startup, so the app self-initializes

- [x] T008 Generate initial migration via `alembic revision --autogenerate -m "initial schema"`
  - This creates `alembic/versions/<rev>_initial_schema.py` with `op.create_table()` calls for all 10 entities
  - Review the generated file against `data-model.md` to verify all tables and columns are present
  - Ensure `Match` table (SQL keyword) is properly quoted in generated DDL

- [x] T009 Apply initial migration to a fresh database via `alembic upgrade head`
  - Remove any existing `match_combat.db` to start clean
  - Run `alembic upgrade head`
  - Verify all 10 tables + `alembic_version` table are created
  - Run `alembic current` and verify it shows the initial revision at `head`

- [x] T010 Update `Dockerfile` to use Python 3.11 (from 3.9)
  - Change `FROM python:3.9` to `FROM python:3.11`
  - This aligns with the constitution's "Python 3.11+" requirement and local dev environment

**Checkpoint**: Foundation ready — Alembic environment is configured, initial migration generated and applied, and the app can self-initialize via `init_db()`.

---

## Phase 3: User Story 1 - Generate and apply database migrations (Priority: P1) 🎯 MVP

**Goal**: A developer can generate migration scripts from model definition changes and apply them to keep the database schema in sync with application code.

**Independent Test**: Modify a SQLModel definition, run the migration generation command, verify a migration script file is created. Apply it to a database and verify the schema updates. Test with multiple pending migrations.

### Implementation for User Story 1

- [x] T011 [US1] Verify initial migration creates all 10 tables on a fresh database
  - Run `alembic upgrade head` on a clean database
  - Inspect the database (e.g., `sqlite3 match_combat.db ".tables"`) and verify all tables exist: `sexo`, `modalidad`, `competidor`, `match`, `evento`, `area`, `entrada`, `user`, `tokenblacklist`, `passwordresettoken`, `alembic_version`
  - Acceptance scenario 4: fresh database with no tables → created with full schema

- [x] T012 [US1] Test model modification: add a field and generate a migration
  - Add a new field to an existing model (e.g., add `apellido` field to `Competidor` in `app/models/competidor.py`)
  - Run `alembic revision --autogenerate -m "add apellido to competidor"`
  - Verify the generated migration script contains the correct `op.add_column(...)` call
  - Acceptance scenario 1: modified model → migration script created capturing the schema change

- [x] T013 [US1] Apply the generated migration and verify schema updates
  - Run `alembic upgrade head` to apply the migration from T012
  - Inspect the modified table and verify the new column exists
  - Acceptance scenario 2: migration script exists → apply command updates schema

- [x] T014 [US1] Verify multiple pending migrations apply in dependency order
  - Create a second model change and generate another migration (`--autogenerate`)
  - Run `alembic upgrade head` and verify both migrations apply sequentially
  - Check `alembic history` shows both revisions in the correct chain order
  - Acceptance scenario 3: multiple pending → all applied in dependency order

**Checkpoint**: At this point, the developer can generate and apply migrations from model changes. Schema stays in sync with code.

---

## Phase 4: User Story 2 - Track migration history and rollback (Priority: P2)

**Goal**: A developer can audit which migrations have been applied and rollback unwanted changes to recover from problematic deployments.

**Independent Test**: Apply migrations to a database, query the migration history table, rollback a specific migration, and verify the schema reverts.

### Implementation for User Story 2

- [x] T015 [US2] Query `alembic_version` table to verify migration tracking
  - After applying migrations (T009), query the `alembic_version` table
  - Verify it contains the current revision identifier
  - Acceptance scenario 1: migrations applied → migration history is queryable

- [x] T016 [US2] Use `alembic current` and `alembic history` to inspect state
  - Run `alembic current` and verify it reports the current revision
  - Run `alembic history` and verify it lists all applied migrations with timestamps and messages
  - Acceptance scenario 1: developer can see which migrations were applied and when

- [x] T017 [US2] Rollback one migration via `alembic downgrade -1` and verify schema reverts
  - Run `alembic downgrade -1`
  - Verify the `alembic_version` table updates to the previous revision
  - Inspect the database and verify the rolled-back change is reverted (e.g., column removed)
  - Acceptance scenario 2: problematic migration applied → rollback reverts schema to previous state

- [x] T018 [US2] Rollback to a specific revision and verify reverted state
  - Run `alembic downgrade <revision_id>` to target a specific previous version
  - Verify schema matches the state at that revision
  - Acceptance scenario 3: latest migration has a bug → rollback to previous version reverts schema

**Checkpoint**: At this point, migration history is fully auditable and rollback works for recovery.

---

## Phase 5: User Story 3 - Initialize database in new environments (Priority: P3)

**Goal**: A developer setting up a new environment can initialize the database schema from migrations, enabling fast onboarding and CI test reliability.

**Independent Test**: Create a fresh database and run the initialization command, then verify the schema is complete and usable.

### Implementation for User Story 3

- [x] T019 [US3] Verify `alembic stamp head` adopts an existing dev database
  - Using the existing `match_combat.db` (created by `create_all`, now matching models):
  - Run `alembic stamp head`
  - Verify the `alembic_version` table is created and set to `head` **without** re-running DDL
  - Verify no errors occur (tables already exist)
  - Acceptance scenario 1: existing database → stamped as current revision

- [x] T020 [US3] Verify app startup initializes database via `alembic upgrade head`
  - Remove existing `match_combat.db`
  - Start the app: `python -m uvicorn app.main:app --reload`
  - Verify the app starts without error (lifespan calls `init_db()` → `alembic upgrade head`)
  - Verify all tables are created and endpoints are functional
  - Acceptance scenario 1: no database exists → initialization command creates full schema

- [x] T021 [US3] Document CI pipeline integration for database initialization
  - Document the CI command sequence: `rm -f <db_file> && alembic upgrade head` (or `alembic stamp head` if using a pre-built image)
  - Reference `contracts/migration-cli.md` for command details
  - Verify that tests can connect and run after initialization
  - Acceptance scenario 2: CI pipeline initializes database → all tests can connect and run

**Checkpoint**: All user stories are now independently functional — migration generation/apply (US1), history tracking/rollback (US2), and environment initialization (US3).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and CI integration

- [x] T022 [P] Verify `.gitignore` handles Alembic artifacts correctly
  - Ensure `__pycache__/` (already in `.gitignore`) covers `alembic/versions/` cached bytecode
  - Ensure migration script files in `alembic/versions/*.py` are **NOT** ignored (must be version-controlled per FR-007)
  - Ensure `*.db` (already in `.gitignore`) covers the dev database file

- [x] T023 Verify `alembic check` passes (no model drift) — documents the CI gate
  - Run `alembic check` after all migrations are applied
  - Verify exit code 0 (models match database schema)
  - This validates SC-001 through SC-005 success criteria from quickstart.md

- [x] T024 Run quickstart.md validation scenarios end-to-end
  - Follow the 6 validation scenarios in `quickstart.md`:
    1. Fresh DB initialization (SC-002, SC-003)
    2. Migration drift detection via `alembic check` (CI gate)
    3. Generate migration from model change (SC-001)
    4. Apply migration (SC-001)
    5. Rollback (SC-004)
    6. Full app startup (integration)
  - Verify each scenario's expected outcome

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1. T003 must complete before T004. T004, T005, T006 must all complete before T008. T008 must complete before T009. T007 depends on T004. T010 is independent.
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2). T012 depends on T011. T013 depends on T012. T014 depends on T013.
- **User Story 2 (Phase 4)**: Depends on US1 (Phase 3). T016 depends on T015. T017 depends on T016. T018 depends on T017.
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2). T020 depends on T019. T021 depends on T020.
- **Polish (Phase 6)**: Depends on all user story phases being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) is complete. No dependencies on other user stories.
- **User Story 2 (P2)**: Depends on US1 (T011–T014) being complete — needs applied migrations and a known-good baseline to test rollback against.
- **User Story 3 (P3)**: Depends on Foundational (Phase 2) and US1 (T009) — needs a working Alembic environment and initial migration to test database initialization.

### Within Each User Story

- T011 (verify initial migration) → T012 (modify model, generate migration) → T013 (apply migration) → T014 (multiple migrations)
- T015 (query alembic_version) → T016 (alembic current/history) → T017 (downgrade -1) → T018 (downgrade to specific rev)
- T019 (stamp head) → T020 (app startup init) → T021 (CI documentation)

### Parallel Opportunities

- **T004, T005, T006** can be created in parallel (different files: `alembic/env.py`, `app/models/__init__.py`, `app/core/config.py`)
- **T010** (Dockerfile) can run in parallel with Phase 2 tasks (independent file)
- **T022** and **T023** can run in parallel (different concerns)
- **T023** and **T024** can run in parallel (different validation scopes)

---

## Parallel Example: Foundational Phase

```bash
# Launch env.py, naming convention, and config.py in parallel:
Task: "Create alembic/env.py with SQLModel metadata wiring and SQLite batch mode"
Task: "Add naming convention to app/models/__init__.py"
Task: "Fix app/core/config.py to honor DB_URL env var"

# Sequential dependencies after parallel setup:
Task: "Generate initial migration via autogenerate"   (depends on all 3 above)
Task: "Apply initial migration to fresh database"      (depends on initial migration)
Task: "Replace create_all with alembic upgrade in database.py"  (depends on env.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install Alembic, init environment)
2. Complete Phase 2: Foundational (env.py, naming convention, config fix, create_all replacement, initial migration)
3. Complete Phase 3: User Story 1 (generate + apply migrations from model changes)
4. **STOP and VALIDATE**: Run quickstart.md Scenario 1–3 (fresh DB init, drift detection, model change migration)
5. Deploy if ready

### Incremental Delivery

1. Foundational → Foundation ready ✓
2. Add User Story 1 (generate + apply) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (history + rollback) → Test independently → Deploy/Demo
4. Add User Story 3 (environment init) → Test independently → Deploy/Demo
5. Polish → CI gate (`alembic check`), full quickstart validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 1 + Phase 2 together (Foundational is shared, blocking)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1 — generate + apply)
   - Developer B: User Story 2 (P2 — tracking + rollback)
   - Developer C: User Story 3 (P3 — environment init)
3. All stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This feature focuses on infrastructure/tooling: no new API endpoints, no new models — only Alembic environment configuration and database.py/config.py refinements
- The `Match` model maps to table name `match` (SQL reserved word) — SQLAlchemy/SQLModel quotes it automatically, but keep this in mind when hand-editing migrations
- The `CriteriosDTO` in `app/models/criterios.py` is a DTO (no `table=True`) and must NOT be imported as a model in `env.py` or `__init__.py`
- Alembic 1.20.0 is the latest compatible version with SQLAlchemy 2.0.15 (research.md R-001)
- Naming convention in `__init__.py` must execute before any model import — place it at the top of the file
- Commit migration scripts alongside application code (FR-007: migration scripts stored as version-controlled files)
