# Feature Specification: JWT Authentication & Authorization

**Feature Branch**: `001-jwt-auth`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Agregar autenticacion y autorizacion con JWT, rol de administrador, login/logout, endpoints protegidos, CRUD de usuarios con recuperacion de password."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Login and Access Protected Resources (Priority: P1)

An administrator opens the application and is presented with a login
screen. They enter their username and password. Upon successful
authentication, the system issues a token that is included in
subsequent requests. The administrator can now access all protected
endpoints (competitors, matches, categories). When the session
expires or the administrator logs out, the token is invalidated and
further requests are rejected until a new login.

**Why this priority**: Without login and token-based protection,
no other auth feature has value. This is the foundational security
gate for the entire system.

**Independent Test**: Can be fully tested by attempting to access
any existing endpoint without a token (rejected), then logging in
and retrying (accepted).

**Acceptance Scenarios**:

1. **Given** a registered administrator with valid credentials,
   **When** they submit their username and password to the login
   endpoint, **Then** the system returns a valid access token and
   a refresh token.
2. **Given** a valid access token, **When** the administrator
   makes a request to any protected endpoint, **Then** the request
   is processed normally.
3. **Given** an expired or invalid token, **When** a request is
   made to a protected endpoint, **Then** the system returns a
   401 Unauthorized response.
4. **Given** a logged-in administrator, **When** they call the
   logout endpoint, **Then** the token is invalidated and
   subsequent requests with that token are rejected.
5. **Given** an expired access token and a valid refresh token,
   **When** the administrator requests a new access token,
   **Then** the system issues a new access token without
   requiring re-login.

---

### User Story 2 - User Management (Priority: P2)

A logged-in administrator can create new administrator accounts
by providing username, password, first name, last name, and email.
They can also view the list of existing users, update user details,
and deactivate accounts. Each user account is unique by username
and email.

**Why this priority**: The system needs a way to manage who has
access. Without user creation, only a pre-seeded account would
exist.

**Independent Test**: Can be tested by logging in with an
existing admin, creating a new user, then logging in with
the new user's credentials.

**Acceptance Scenarios**:

1. **Given** a logged-in administrator, **When** they submit
   valid user details (username, password, first name, last
   name, email), **Then** a new user account is created and
   a confirmation is returned.
2. **Given** a logged-in administrator, **When** they attempt
   to create a user with a duplicate username or email,
   **Then** the system rejects the request with a clear error.
3. **Given** a logged-in administrator, **When** they request
   the list of users, **Then** the system returns all registered
   users (without exposing passwords).
4. **Given** a logged-in administrator, **When** they update
   another user's profile information, **Then** the changes
   are persisted.

---

### User Story 3 - Password Recovery (Priority: P3)

An administrator who has forgotten their password can request a
password reset. The system sends a time-limited reset link to
the email associated with their account. The administrator clicks
the link and sets a new password.

**Why this priority**: Important for operational continuity but
not a launch blocker since passwords can initially be reset
manually by another admin.

**Independent Test**: Can be tested by requesting a reset for
a known email, verifying the reset token is generated, and
using it to set a new password.

**Acceptance Scenarios**:

1. **Given** a user with a registered email, **When** they
   request a password reset providing their email, **Then**
   the system generates a time-limited reset token and sends
   a reset link to that email.
2. **Given** a valid reset token, **When** the user submits
   a new password, **Then** the password is updated and the
   reset token is invalidated.
3. **Given** an expired or already-used reset token, **When**
   the user attempts to reset their password, **Then** the
   system rejects the request with a clear error.
4. **Given** an email that does not exist in the system,
   **When** someone requests a password reset, **Then** the
   system responds with the same success message (to prevent
   user enumeration).

---

### Edge Cases

- What happens when a user tries to log in with a correct
  username but wrong password multiple times? The system MUST
  lock the account after 5 consecutive failed attempts for
  15 minutes.
- What happens when a token is used after logout? The system
  MUST reject it with 401 Unauthorized.
- What happens when the refresh token expires? The user MUST
  re-authenticate with username and password.
- What happens when an administrator tries to delete their own
  account? The system MUST prevent self-deletion if it would
  leave zero active administrators.
- What happens when password reset is requested for a
  non-existent email? The system MUST respond identically to
  a valid request (no information leakage).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow administrators to log in with
  username and password, receiving an access token and a
  refresh token upon success.
- **FR-002**: System MUST protect all existing endpoints
  (`/api/competidor`, `/api/modalidad`, `/api/match`) so that
  only requests with a valid access token are accepted.
  The `/api/ping` endpoint MUST remain public.
- **FR-003**: System MUST support logout by invalidating the
  current access token.
- **FR-004**: System MUST support token refresh: given a valid
  refresh token, issue a new access token without requiring
  re-login.
- **FR-005**: System MUST allow a logged-in administrator to
  create new user accounts with: username (unique), password,
  first name, last name, and email (unique).
- **FR-006**: System MUST store passwords securely using a
  one-way hashing algorithm; plaintext passwords MUST never
  be stored or returned.
- **FR-007**: System MUST allow listing all users and viewing
  individual user details (excluding password).
- **FR-008**: System MUST allow updating user profile fields
  (first name, last name, email) for any user.
- **FR-009**: System MUST support password recovery via a
  time-limited reset token sent to the user's registered email.
- **FR-010**: System MUST lock accounts after 5 consecutive
  failed login attempts for a duration of 15 minutes.
- **FR-011**: System MUST include a single role: administrator.
  All authenticated users have full access to all endpoints.
- **FR-012**: Access tokens MUST have a configurable expiration
  time (default: 30 minutes). Refresh tokens MUST have a longer
  expiration (default: 7 days).
- **FR-013**: The login and password-reset endpoints MUST be
  accessible without authentication.
- **FR-014**: System MUST provide a way to create an initial
  administrator account (seed) when no users exist in the
  system.

### Key Entities

- **User**: Represents an administrator account. Attributes:
  username, hashed password, first name, last name, email,
  active status, failed login attempts count, last failed login
  timestamp, creation date.
- **Token Blacklist**: Tracks invalidated tokens (from logout)
  to prevent reuse. Attributes: token identifier, expiration
  timestamp.
- **Password Reset Token**: A time-limited token associated
  with a user for password recovery. Attributes: token value,
  user reference, expiration timestamp, used status.

### Assumptions

- Only one role (administrator) exists; role-based access
  control expansion is not in scope for this feature.
- Email delivery for password recovery relies on an external
  SMTP service configured via environment variables.
- The existing `/api/ping` health check endpoint remains
  public and unprotected.
- The initial admin account is created via a seed mechanism
  (CLI command or automatic on first startup) rather than a
  public registration endpoint.
- There is no public user self-registration; only existing
  administrators can create new users.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Unauthenticated requests to protected endpoints
  are rejected 100% of the time with a clear unauthorized
  response.
- **SC-002**: Administrators can complete the login flow
  (enter credentials, receive token, access protected resource)
  in under 30 seconds.
- **SC-003**: Password recovery flow (request reset, receive
  email, set new password, log in) completes successfully
  within 5 minutes of the email being received.
- **SC-004**: After logout, the invalidated token is rejected
  on all subsequent requests with zero exceptions.
- **SC-005**: Account lockout activates after exactly 5 failed
  attempts and automatically unlocks after 15 minutes.
- **SC-006**: All existing functionality (competitors, matches,
  categories) continues to work identically for authenticated
  users with no regressions.
