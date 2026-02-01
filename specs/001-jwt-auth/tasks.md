# Tasks: JWT Authentication & Authorization

**Input**: Design documents from `/specs/001-jwt-auth/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Install dependencies and add configuration variables

- [x] T001 Add python-jose[cryptography], passlib[bcrypt], and python-multipart to requirements.txt
- [x] T002 Add JWT and SMTP configuration variables to app/core/config.py: JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES (default 30), JWT_REFRESH_TOKEN_EXPIRE_DAYS (default 7), ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_USE_TLS, PASSWORD_RESET_EXPIRE_HOURS
- [x] T003 Add JWT and SMTP environment variables to .env with development defaults

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Models, security infrastructure, and admin seed that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create User model (SQLModel, table=True) in app/models/user.py with fields: id, username (unique), email (unique), hashed_password, nombre, apellido, is_active (default True), failed_login_attempts (default 0), last_failed_login_at (nullable), created_at (default now). Follow the existing SQLModel pattern from app/models/competidor.py
- [x] T005 [P] Create TokenBlacklist model (SQLModel, table=True) in app/models/user.py with fields: id, jti (unique, indexed), expires_at, created_at (default now)
- [x] T006 [P] Create PasswordResetToken model (SQLModel, table=True) in app/models/user.py with fields: id, token (unique, indexed), user_id (FK → User.id), expires_at, used (default False), created_at (default now). Add Relationship to User
- [x] T007 Replace app/core/security/providers.py with password hashing utilities: create a CryptContext instance using bcrypt scheme, and functions verify_password(plain, hashed) and get_password_hash(password). Remove all Cognito/Auth0 code
- [x] T008 Replace app/core/security/base.py with JWT utility functions: create_access_token(data, expires_delta), create_refresh_token(data, expires_delta), decode_token(token). Use python-jose with HS256 algorithm. Include jti (uuid4) and type ("access"/"refresh") claims. Read JWT_SECRET_KEY from config. Remove all BaseAuth, CognitoAuth, Auth0Auth, JWTBearer, and AuthUser classes
- [x] T009 Implement get_current_user dependency in app/core/security/deps.py: extract Bearer token from Authorization header using FastAPI's OAuth2PasswordBearer, decode it, verify type is "access", check jti is not in TokenBlacklist table, load User from DB by sub claim, raise 401 if any step fails. Return User instance
- [x] T010 Replace app/core/security/authentication.py: remove API key validation code and auth_required decorator. File can be left empty or deleted
- [x] T011 Create auth DTOs in app/entities/auth_entities.py: TokenResponse (access_token, refresh_token, token_type), RefreshTokenRequest (refresh_token), RefreshTokenResponse (access_token, token_type), PasswordResetRequest (email), PasswordResetConfirm (token, new_password). Use Pydantic BaseModel following the pattern in app/entities/match_entities.py
- [x] T012 [P] Create user DTOs in app/entities/user_entities.py: UserCreateDTO (username, password, email, nombre, apellido), UserUpdateDTO (nombre optional, apellido optional, email optional, is_active optional), UserResponse (id, username, email, nombre, apellido, is_active, created_at — excludes password). Use Pydantic BaseModel
- [x] T013 Modify app/core/database.py: after init_db() creates tables, add seed_admin() function that checks if any User exists, and if not, creates one using ADMIN_USERNAME, ADMIN_PASSWORD (hashed), ADMIN_EMAIL from config. Call seed_admin() in the lifespan after init_db(). Log a message when the admin is created
- [x] T014 Update app/api/routes/router.py: add auth_controller router with prefix "/api/auth" and tags ["auth"], add user_controller router with prefix "/api/user" and tags ["user"]. Apply get_current_user dependency to competidor, modalidad, and match routers (not ping, not auth). Use APIRouter(dependencies=[Depends(get_current_user)]) or apply at include_router level

**Checkpoint**: Foundation ready — User, TokenBlacklist, PasswordResetToken tables created, JWT utilities available, admin seeded, routes wired with auth dependency

---

## Phase 3: User Story 1 - Login and Access Protected Resources (Priority: P1)

**Goal**: Administrators can log in with username/password, receive JWT tokens, access protected endpoints, refresh tokens, and log out

**Independent Test**: Access any endpoint without token (401), login, retry with token (200), logout, retry (401)

### Implementation for User Story 1

- [x] T015 [P] [US1] Create auth_service.py in app/services/auth_service.py with authenticate_user(username, password, session) function: look up user by username, verify password with verify_password(), check account lockout (failed_login_attempts >= 5 and last_failed_login_at within 15 minutes → raise 423), on failure increment failed_login_attempts and set last_failed_login_at, on success reset failed_login_attempts to 0 and return User
- [x] T016 [US1] Add login function to app/services/auth_service.py: call authenticate_user(), generate access_token and refresh_token using create_access_token/create_refresh_token from security/base.py, return TokenResponse DTO
- [x] T017 [US1] Add logout function to app/services/auth_service.py: decode the current token, extract jti and exp, insert into TokenBlacklist table, commit
- [x] T018 [US1] Add refresh function to app/services/auth_service.py: decode refresh token, verify type is "refresh", check jti not in blacklist, load user from DB, generate new access token, return RefreshTokenResponse
- [x] T019 [US1] Create auth_controller.py in app/controllers/auth_controller.py with routes: POST /login (public, uses OAuth2PasswordRequestForm, calls auth_service.login), POST /logout (protected via get_current_user, calls auth_service.logout), POST /refresh (public, accepts RefreshTokenRequest body, calls auth_service.refresh). Delegate all logic to auth_service. Follow controller pattern from app/controllers/match_controller.py
- [x] T020 [US1] Verify existing endpoints are protected: confirm that GET /api/competidor/, GET /api/modalidad/, POST /api/match/ return 401 without a token, and GET /api/ping returns 200 without a token. This is a manual verification step after T014 wiring is complete

**Checkpoint**: Login, logout, token refresh, and endpoint protection are fully functional. User Story 1 is independently testable.

---

## Phase 4: User Story 2 - User Management (Priority: P2)

**Goal**: Logged-in administrators can create, list, view, and update user accounts

**Independent Test**: Login as seeded admin, create a new user, list users (see both), update user's email, login as the new user

### Implementation for User Story 2

- [x] T021 [P] [US2] Create user_service.py in app/services/user_service.py with functions: create_user(user_data: UserCreateDTO, session) — hash password, check uniqueness of username/email (raise 409 ConflictException if duplicate), create User, return UserResponse. get_all_users(session) — return list of all users. get_user_by_id(user_id, session) — return user or raise 404. update_user(user_id, user_data: UserUpdateDTO, session) — update fields, check email uniqueness if changed, return UserResponse
- [x] T022 [US2] Create user_controller.py in app/controllers/user_controller.py with routes: GET / (list users), GET /{user_id} (get single user), POST / (create user, status 201), PATCH /{user_id} (update user). All routes are protected (dependency applied at router level in T014). Delegate all logic to user_service. Follow controller pattern from app/controllers/competidor_controller.py

**Checkpoint**: User CRUD is fully functional. User Story 2 is independently testable.

---

## Phase 5: User Story 3 - Password Recovery (Priority: P3)

**Goal**: Administrators can request a password reset via email and set a new password using a time-limited token

**Independent Test**: Request reset for known email, verify token generated in DB, use token to set new password, login with new password

### Implementation for User Story 3

- [x] T023 [P] [US3] Create email_service.py in app/services/email_service.py with send_password_reset_email(to_email, reset_token) function: use smtplib to send an email containing the reset token/link. Read SMTP config from config.py. Handle connection errors gracefully (log error, do not crash). Use SMTP_USE_TLS for STARTTLS
- [x] T024 [US3] Add password reset request function to app/services/auth_service.py: look up user by email, if found generate a UUID token, create PasswordResetToken record with expiration (PASSWORD_RESET_EXPIRE_HOURS from config), call email_service.send_password_reset_email(). Always return the same success message regardless of whether the email exists (prevent enumeration)
- [x] T025 [US3] Add password reset confirm function to app/services/auth_service.py: look up PasswordResetToken by token value, verify not used and not expired (raise 400 BadRequestException if invalid), hash new password, update User.hashed_password, set token.used = True, commit in single transaction
- [x] T026 [US3] Add password reset routes to app/controllers/auth_controller.py: POST /password-reset/request (public, accepts PasswordResetRequest body, calls auth_service password reset request function), POST /password-reset/confirm (public, accepts PasswordResetConfirm body, calls auth_service password reset confirm function)

**Checkpoint**: Password recovery flow is fully functional. User Story 3 is independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, edge cases, and final validation

- [x] T027 [P] Clean up expired TokenBlacklist entries: add a cleanup_expired_tokens(session) function in app/services/auth_service.py that deletes rows where expires_at < now(). Call it from the lifespan startup in app/main.py after seed_admin()
- [x] T028 [P] Add self-deletion guard to user_service.py: if an admin deactivates their own account and they are the last active admin, raise a 400 BadRequestException with message "Cannot deactivate the last active administrator"
- [x] T029 Remove unused files and imports: delete app/core/security/providers.py if not already replaced, remove any remaining references to cognitojwt, auth0, UserProfile, API_KEY_NAME, get_user_using_apikey from across the codebase. Clean up app/repositories/base_respository.py import of app.models.user.User if it causes import errors
- [x] T030 Run quickstart.md verification checklist in specs/001-jwt-auth/quickstart.md: manually test all curl commands to confirm login, protected access, logout, user creation, and password reset work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion. Can run in parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational phase completion. Can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### Within Each User Story

- Models before services (handled in Foundational)
- Services before controllers
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T005, T006 can run in parallel with T004 (different models, same file but independent sections)
- T007, T008 can run in parallel (different files in security/)
- T011, T012 can run in parallel (different DTO files)
- T015, T021, T023 can run in parallel (different service files, different stories)
- T027, T028, T029 can run in parallel (different concerns)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T014)
3. Complete Phase 3: User Story 1 (T015–T020)
4. **STOP and VALIDATE**: Login, logout, token refresh, endpoint protection all work
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Polish phase → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The existing Cognito/Auth0 security code is replaced, not extended
