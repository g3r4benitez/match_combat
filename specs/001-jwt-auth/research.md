# Research: JWT Authentication & Authorization

## R1: JWT Library Choice

**Decision**: python-jose[cryptography]
**Rationale**: Most widely used JWT library in the FastAPI ecosystem.
FastAPI's official documentation recommends it. Supports HS256
(symmetric, sufficient for single-service API) and RS256 if needed
later. The `[cryptography]` extra provides the recommended backend.
**Alternatives considered**:
- PyJWT: Also popular but python-jose has better FastAPI ecosystem
  integration and is recommended in FastAPI docs.
- authlib: More comprehensive but heavier; violates Simplicity/YAGNI
  principle for a single-role local auth system.

## R2: Password Hashing

**Decision**: passlib[bcrypt] with CryptContext
**Rationale**: Industry standard for password hashing. bcrypt is
resistant to brute-force attacks with configurable work factor.
passlib's CryptContext provides a clean API and supports automatic
scheme migration if the hashing algorithm changes in the future.
**Alternatives considered**:
- argon2-cffi: Stronger against GPU attacks but bcrypt is sufficient
  for a small admin user base (< 50 users). Adds native dependency
  complexity.
- hashlib (stdlib): Not suitable for password hashing; lacks salt
  management and work factor control.

## R3: Token Invalidation Strategy (Logout)

**Decision**: Database-backed token blacklist with JTI claim
**Rationale**: Each JWT includes a unique `jti` (JWT ID) claim.
On logout, the `jti` is inserted into a `TokenBlacklist` table.
Token validation checks the blacklist. Expired blacklist entries
are periodically cleaned up (can be done on startup or via a
scheduled task). This approach is simple and works with the existing
PostgreSQL/SQLite database.
**Alternatives considered**:
- Redis-based blacklist: Faster lookup but adds infrastructure
  dependency. The project has Redis in requirements but only for
  Celery. Using the database keeps things simpler for a small user
  base.
- Short-lived tokens only (no blacklist): Does not satisfy FR-003
  (logout must immediately invalidate tokens).

## R4: Token Refresh Strategy

**Decision**: Separate refresh token stored as JWT with longer
expiration, different `type` claim ("refresh" vs "access")
**Rationale**: Refresh tokens allow extending sessions without
re-entering credentials. Both access and refresh tokens are JWTs
signed with the same secret but distinguished by a `type` claim.
The refresh endpoint validates the refresh token and issues a new
access token. Refresh tokens are also blacklisted on logout.
**Alternatives considered**:
- Opaque refresh tokens stored in DB: More secure against token
  theft but adds complexity. For a small admin API, JWT-based
  refresh is sufficient.
- Sliding window (extend access token on each request): Does not
  provide clear session boundaries for security auditing.

## R5: Password Recovery Email Delivery

**Decision**: SMTP via Python's `smtplib` with environment-variable
configuration (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
SMTP_FROM_EMAIL)
**Rationale**: Standard approach; no external service dependency
beyond an SMTP server. Can work with Gmail, SendGrid, AWS SES, or
any SMTP-compatible provider. Configuration via environment
variables follows the existing pattern in `config.py`.
**Alternatives considered**:
- SendGrid/Mailgun SDK: Vendor lock-in. SMTP is universal.
- Celery background task for email: The project has Celery
  configured but for a simple reset email, synchronous sending
  is acceptable. Can be moved to Celery later if needed.

## R6: Account Lockout Implementation

**Decision**: Track `failed_login_attempts` and
`last_failed_login_at` fields on the User model. After 5
consecutive failures, reject login for 15 minutes. Successful login
resets the counter to 0.
**Rationale**: Simple, database-backed approach. No external
dependencies. The 15-minute window is calculated by comparing
`last_failed_login_at` with current time. No need for a separate
lockout table or cache.
**Alternatives considered**:
- Redis-based rate limiting: Overkill for < 50 users.
- IP-based rate limiting: Does not protect against credential
  stuffing from distributed IPs; account-level lockout is more
  appropriate.

## R7: Initial Admin Seed

**Decision**: Auto-create admin on first startup if no users exist
in the database. Credentials read from environment variables
(ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL). Log a warning if
defaults are used.
**Rationale**: Simplest approach for bootstrapping. Fits the
existing `init_db()` lifespan pattern in `main.py`. No CLI command
needed.
**Alternatives considered**:
- CLI command (`python -m app.seed`): More explicit but requires
  manual step during deployment. Can be added later if needed.
- Migration script: Mixes schema and data concerns.

## R8: Existing Security Code Disposition

**Decision**: Replace `app/core/security/providers.py` (Cognito and
Auth0 implementations) and `app/core/security/base.py` (abstract
BaseAuth, JWTBearer, AuthUser) with a simplified local JWT
implementation. Remove unused imports to `cognitojwt`, `auth0`,
and `UserProfile`. Keep the authentication exceptions as they
are already well-structured.
**Rationale**: The existing security code references external
identity providers (Cognito, Auth0) that are not in use and have
missing dependencies. Replacing rather than extending avoids dead
code and aligns with the Simplicity principle.
**Alternatives considered**:
- Extend BaseAuth with a LocalAuth provider: Would preserve the
  provider pattern but the abstraction adds complexity without
  value since only one provider (local) is needed.
