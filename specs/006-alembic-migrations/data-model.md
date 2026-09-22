# Data Model: Alembic Migrations

**Feature**: 006-alembic-migrations
**Date**: 2026-09-21

## Overview

This feature introduces Alembic as the database migration tool. It **does not alter** the existing data model — it formalizes the management of the schema already defined by the SQLModel entities in `app/models/`. All existing entities below are tracked by `SQLModel.metadata` and will be covered by an initial Alembic migration.

The new entity introduced by this feature is **MigrationHistory** — Alembic's internal `alembic_version` table that tracks which migration revisions have been applied.

## Existing Entities (tracked by Alembic autogenerate)

### Sexo

Lookup table for competitor genders.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| name | String | NOT NULL | Gender name (e.g., "Masculino", "Femenino") |

**Relationships**: Has many `Competidor` (via `sexo_id` FK).

### Modalidad

Lookup table for competition categories/modalities.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| name | String | NOT NULL | Modality name |
| evento_id | Integer | FK → evento.id, nullable | Owning event |

**Relationships**: Many-to-one `Evento`; has many `Competidor` and `Match`.

### Competidor

A competitor registered for an event.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| nombre | String | NOT NULL | First name |
| edad | Integer | NOT NULL | Age in years |
| peso | Float | NOT NULL | Weight |
| escuela | String | NOT NULL | School/team name |
| evento_id | Integer | FK → evento.id, nullable | Owning event |
| modalidad_id | Integer | FK → modalidad.id, nullable | Assigned modality |
| sexo_id | Integer | FK → sexo.id, nullable | Gender |
| matched | Boolean | default: `False` | Set `true` when matched in a Match |
| historial | Integer | NOT NULL | Fight history count |
| historial_str | String | nullable | History description string |
| comentarios | String | nullable | Comments |

**Relationships**: Many-to-one each to `Evento`, `Modalidad`, `Sexo`; has many `Match` (as first or second competitor).

**Constitution note (Domain Integrity)**: `matched` field MUST only be set to `true` when a `Match` record links this competitor; deleting a `Match` resets `matched` to `false`.

### Match

A match/fight between two competitors.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| competidor_1_id | Integer | FK → competidor.id, NOT NULL | First competitor |
| competidor_2_id | Integer | FK → competidor.id, NOT NULL | Second competitor |
| modalidad_id | Integer | FK → modalidad.id, nullable | Match modality |
| evento_id | Integer | FK → evento.id, nullable | Owning event |
| area_id | Integer | FK → area.id, nullable | Competition area |
| comentarios | String | default: `""` | Comments |
| orden | Integer | default: `0` | Display order (must be unique/consistent) |
| completada | Boolean | default: `False` | Whether the match is completed |

**Relationships**: Many-to-one each to `Competidor` (x2 via `primaryjoin`), `Modalidad`, `Evento`, `Area`.

**Constitution note (Data Consistency)**: `orden` MUST remain unique and consistent after any reordering operation.

### Evento

A contact sport event (e.g., "Beast Wars 2da Edición").

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| nombre | String | NOT NULL | Event name |
| fecha | Date | NOT NULL | Event date |
| activo | Boolean | default: `True` | Whether event is active |

**Relationships**: Has many `Area`, `Modalidad`, `Competidor`, `Match`, `Entrada`.

### Area

A competition area/court within an event.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| nombre | String | NOT NULL | Area name |
| evento_id | Integer | FK → evento.id, NOT NULL | Owning event |

**Relationships**: Many-to-one `Evento`; has many `Match`.

### Entrada

A ticket/entry for an event.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| nombre | String | NOT NULL | Entry holder name |
| escuela | String | NOT NULL | School/team name |
| usada | Integer | default: `0` | Usage flag (0/1) |
| uuid | String | unique, auto-generated | UUID4 via `uuid.uuid4()` |
| evento_id | Integer | FK → evento.id, nullable | Owning event |

**Relationships**: Many-to-one `Evento`.

**Note**: From feature 004-entrada-nombre-unico, the `nombre` field may have a uniqueness constraint. See migration considerations.

### User

An application user (authentication principal).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| username | String(50) | unique, indexed, NOT NULL | Username |
| email | String(255) | unique, indexed, NOT NULL | Email |
| hashed_password | String(255) | NOT NULL | Password hash |
| nombre | String(100) | NOT NULL | First name |
| apellido | String(100) | NOT NULL | Last name |
| is_active | Boolean | default: `True` | Account active flag |
| failed_login_attempts | Integer | default: `0` | Failed login counter |
| last_failed_login_at | DateTime | nullable | Last failed login timestamp |
| created_at | DateTime | default: `datetime.utcnow()` | Creation timestamp |

**Relationships**: Has many `PasswordResetToken`.

### TokenBlacklist

Blacklisted JWT tokens (for logout/invalidation).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| jti | String(255) | unique, indexed, NOT NULL | JWT ID |
| expires_at | DateTime | NOT NULL | Expiration timestamp |
| created_at | DateTime | default: `datetime.utcnow()` | Creation timestamp |

### PasswordResetToken

Password reset tokens.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Primary key |
| token | String(255) | unique, indexed, NOT NULL | Reset token string |
| user_id | Integer | FK → user.id, NOT NULL | Associated user |
| expires_at | DateTime | NOT NULL | Expiration timestamp |
| used | Boolean | default: `False` | Whether token has been used |
| created_at | DateTime | default: `datetime.utcnow()` | Creation timestamp |

**Relationships**: Many-to-one `User`.

## New Entity Introduced by This Feature

### MigrationHistory (alembic_version)

Alembic's internal tracking table. Automatically managed by Alembic — **not** defined in application models.

| Field | Type | Description |
|-------|------|-------------|
| version_num | String(32) | Current migration revision identifier |

**Behavior**:
- Created automatically by Alembic on first migration.
- Stores a single row representing the current database revision.
- `alembic upgrade head` updates this to the target revision.
- `alembic downgrade` updates this to the previous revision.
- `alembic stamp head` sets the version without running DDL.

## Schema Evolution Considerations for Migrations

### Foreign Key Constraints (Constitution IV)
All foreign keys defined in SQLModel models via `Field(foreign_key=...)` are enforced at the database level. Alembic autogenerate will produce `ForeignKeyConstraint` in migrations. The naming convention (research.md R-006) assigns deterministic names for proper SQLite batch reflection.

### Enum / Lookup Tables
The `Sexo` and `Modalidad` tables are **lookup tables** (not database ENUM types). Adding/removing lookup entries is data, not schema — handled by data migrations (custom `upgrade()` code inserting/deleting rows), not autogenerate.

### `match` Table Name
SQLAlchemy/SQLModel quotes the `match` identifier (reserved keyword in SQL). Alembic handles this correctly in generated migrations, but manual edits must preserve quoting.

### Constraint Naming (Migration Safety)
- **Before migration feature**: Unnamed FKs, constraints with implicit names.
- **After migration feature**: Naming convention applied to `SQLModel.metadata` ensures all constraints get deterministic names, enabling safe SQLite batch operations on schema changes.

## Relationships Diagram (Logical)

```
Evento (1) ───< Area
Evento (1) ───< Modalidad
Evento (1) ───< Competidor
Evento (1) ───< Match
Evento (1) ───< Entrada

Sexo (1) ───< Competidor
Modalidad (1) ───< Competidor
Modalidad (1) ───< Match

Competidor (1) ───< Match.competidor_1_id
Competidor (1) ───< Match.competidor_2_id
Area (1) ───< Match

User (1) ───< PasswordResetToken
```

## Validation Rules

| Entity | Field | Rule | Source |
|--------|-------|------|--------|
| Competidor | matched | Only `true` when a Match links it | Constitution II |
| Competidor | historial | Must be integer ≥ 0 | Model definition |
| Match | orden | Must be unique and consistent after reordering | Constitution IV |
| Entrada | uuid | Must be unique | Model definition (Field unique=True) |
| User | username | Unique, max 50 chars | Model definition |
| User | email | Unique, max 255 chars | Model definition |
| TokenBlacklist | jti | Unique | Model definition |
| PasswordResetToken | token | Unique | Model definition |
