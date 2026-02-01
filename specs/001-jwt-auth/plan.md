# Implementation Plan: JWT Authentication & Authorization

**Branch**: `001-jwt-auth` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jwt-auth/spec.md`

## Summary

Add local JWT-based authentication and authorization to the Match
Combat API. All existing endpoints (competidor, modalidad, match)
will require a valid Bearer token. The system introduces a User
model, login/logout endpoints, token refresh, user CRUD for
administrators, and password recovery via email. The existing
partial security infrastructure (Cognito/Auth0 providers) will be
replaced with a self-contained local JWT implementation using
python-jose and passlib.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.112.0, SQLModel 0.0.22,
python-jose[cryptography] (JWT), passlib[bcrypt] (password hashing),
python-multipart (form data for OAuth2PasswordRequestForm)
**Storage**: PostgreSQL (production), SQLite (development) via SQLModel
**Testing**: pytest with httpx
**Target Platform**: Linux server (Docker)
**Project Type**: Single project (API only)
**Performance Goals**: Login response < 500ms, token validation < 50ms
**Constraints**: Stateless JWT with blacklist for logout; SMTP for
password recovery emails
**Scale/Scope**: Small admin team (< 50 users), single role

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | Auth endpoints follow `/api/auth/` prefix. DTOs defined before implementation. Controllers delegate to services. |
| II. Domain Integrity | PASS | Auth is a separate domain; does not alter matching logic. |
| III. Layered Architecture | PASS | auth_controller → auth_service → user_repository → User model. No layer skipping. |
| IV. Data Consistency | PASS | User creation and token blacklisting are single-entity operations. Password reset token lifecycle managed in transactions. |
| V. Simplicity and YAGNI | PASS | Single role (no RBAC framework). Local JWT (no external IdP). Replaces unused Cognito/Auth0 code. New dependencies justified: python-jose (JWT encode/decode), passlib (bcrypt hashing), python-multipart (form parsing). |

## Project Structure

### Documentation (this feature)

```text
specs/001-jwt-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── auth-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── controllers/
│   └── auth_controller.py       # NEW: login, logout, refresh, password reset
│   └── user_controller.py       # NEW: user CRUD
├── services/
│   └── auth_service.py          # NEW: authentication logic
│   └── user_service.py          # NEW: user management logic
│   └── email_service.py         # NEW: email sending for password reset
├── models/
│   └── user.py                  # NEW: User, TokenBlacklist, PasswordResetToken
├── entities/
│   └── auth_entities.py         # NEW: login/token DTOs
│   └── user_entities.py         # NEW: user CRUD DTOs
├── repositories/
│   └── user_repository.py       # NEW: user data access
├── core/
│   ├── config.py                # MODIFIED: add JWT and SMTP config vars
│   ├── database.py              # MODIFIED: seed initial admin on startup
│   └── security/
│       └── deps.py              # MODIFIED: JWT dependency for route protection
│       └── base.py              # REPLACED: local JWT provider
│       └── authentication.py    # REPLACED: local JWT validation
│       └── providers.py         # REMOVED: Cognito/Auth0 no longer needed
├── api/routes/
│   └── router.py                # MODIFIED: add auth and user routers
```

**Structure Decision**: Follows existing single-project layout under
`app/`. New files added alongside existing ones in their respective
layer directories. No structural changes needed.

## Complexity Tracking

> No constitution violations. No complexity justifications needed.
