<!--
  Sync Impact Report
  ===================================================================
  Version change: N/A (initial) → 1.0.0
  Modified principles: N/A (first ratification)
  Added sections:
    - Core Principles (5 principles)
    - Technical Constraints
    - Development Workflow
    - Governance
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ reviewed (no changes needed)
    - .specify/templates/spec-template.md ✅ reviewed (no changes needed)
    - .specify/templates/tasks-template.md ✅ reviewed (no changes needed)
  Follow-up TODOs: None
  ===================================================================
-->

# Match Combat Constitution

## Core Principles

### I. API-First Design

Every feature MUST be exposed as a RESTful endpoint through
FastAPI. Endpoints MUST follow the existing prefix convention
(`/api/<resource>/`). Request and response schemas MUST be
defined as Pydantic/SQLModel DTOs before implementation begins.
No business logic is permitted in controllers; controllers
MUST delegate to services.

### II. Domain Integrity

The matching domain is the core of the system. Matching criteria
(sexo, edad, peso, historial, modalidad) MUST be enforced at the
service layer, never at the controller or repository layer.
A Competidor's `matched` field MUST only be set to `true` when
a Match record is successfully created linking that competitor.
Deleting a Match MUST reset `matched` to `false` for both
competitors. Category (Modalidad) boundaries MUST be respected
by default; cross-category matching is only allowed when
explicitly requested via `include_others`.

### III. Layered Architecture

The codebase MUST maintain strict separation into layers:
Controllers → Services → Repositories → Models. Dependencies
flow inward only. Controllers handle HTTP concerns (request
parsing, response formatting, status codes). Services contain
business logic and orchestration. Repositories encapsulate
data access. Models define the domain schema via SQLModel.
No layer may skip an adjacent layer (e.g., controllers MUST NOT
access repositories directly).

### IV. Data Consistency

All state mutations that affect multiple entities (e.g., creating
a Match updates two Competidor records) MUST be executed within
a single database transaction. CSV import operations MUST
validate all rows before persisting any records. Foreign key
constraints MUST be enforced at the database level. The `orden`
field on Match MUST remain unique and consistent after any
reordering operation.

### V. Simplicity and YAGNI

Features MUST only be implemented when explicitly required.
No speculative abstractions, premature optimizations, or
framework additions beyond what the current feature set demands.
Configuration MUST use environment variables via a single
config module. Dependencies MUST be justified; unused
dependencies MUST be removed.

## Technical Constraints

- **Language**: Python 3.11+
- **Framework**: FastAPI with Uvicorn ASGI server
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (production), SQLite (development)
- **Testing**: pytest with httpx for endpoint testing
- **Containerization**: Docker Compose for local services
- **Data format**: JSON for API responses, CSV for bulk
  import/export via Pandas
- **CORS**: Enabled; production deployments MUST restrict
  allowed origins to known frontends

## Development Workflow

- All changes MUST be validated against the existing API
  contract before merging.
- New endpoints MUST include request/response DTO definitions.
- Database schema changes MUST be backward-compatible or
  accompanied by a migration strategy.
- Environment-specific configuration (DB credentials, ports)
  MUST NOT be hardcoded; use `.env` and `app/core/config.py`.
- Commits MUST be atomic and descriptive, covering one logical
  change per commit.

## Governance

This constitution is the authoritative reference for
architectural and development decisions in Match Combat.
All code reviews MUST verify compliance with these principles.

**Amendment procedure**: Any principle change requires
documentation of the rationale, impact analysis on existing
code, and a version bump following semantic versioning:
- MAJOR: Removal or incompatible redefinition of a principle.
- MINOR: New principle added or existing principle materially
  expanded.
- PATCH: Clarifications, wording, or non-semantic refinements.

**Compliance review**: Each pull request MUST include a
self-check against the Core Principles. Violations MUST be
documented in a Complexity Tracking table with justification.

**Version**: 1.0.0 | **Ratified**: 2026-01-29 | **Last Amended**: 2026-01-29
