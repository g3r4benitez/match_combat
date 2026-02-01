# Data Model: JWT Authentication & Authorization

## Entities

### User

Represents an administrator account in the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique identifier |
| username | String(50) | Unique, not null | Login username |
| email | String(255) | Unique, not null | Email address for password recovery |
| hashed_password | String(255) | Not null | bcrypt-hashed password |
| nombre | String(100) | Not null | First name |
| apellido | String(100) | Not null | Last name |
| is_active | Boolean | Default: True | Account active status |
| failed_login_attempts | Integer | Default: 0 | Consecutive failed login count |
| last_failed_login_at | DateTime | Nullable | Timestamp of last failed login |
| created_at | DateTime | Default: now | Account creation timestamp |

**Indexes**: unique on `username`, unique on `email`

**Validation rules**:
- `username`: 3-50 characters, alphanumeric + underscore
- `email`: valid email format
- `password` (input only): minimum 8 characters
- `nombre`, `apellido`: 1-100 characters

**State transitions**:
- Active → Locked: after 5 consecutive failed logins
- Locked → Active: after 15-minute cooldown expires
- Active → Inactive: admin sets `is_active = False`
- Inactive → Active: admin sets `is_active = True`

### TokenBlacklist

Tracks invalidated JWT tokens (from logout) to prevent reuse.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique identifier |
| jti | String(255) | Unique, not null, indexed | JWT ID claim from the token |
| expires_at | DateTime | Not null | Token expiration time (for cleanup) |
| created_at | DateTime | Default: now | When the token was blacklisted |

**Cleanup**: Entries where `expires_at < now()` can be deleted
periodically (on startup or via scheduled task).

### PasswordResetToken

Time-limited token for password recovery.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique identifier |
| token | String(255) | Unique, not null, indexed | Reset token value (UUID or random string) |
| user_id | Integer | FK → User.id, not null | User requesting the reset |
| expires_at | DateTime | Not null | Token expiration (default: 1 hour from creation) |
| used | Boolean | Default: False | Whether the token has been consumed |
| created_at | DateTime | Default: now | When the token was generated |

**Validation rules**:
- Token is valid only if `used == False` and `expires_at > now()`
- Using a token sets `used = True` in the same transaction as the
  password update

## Relationships

```text
User (1) ──── (N) PasswordResetToken
  │
  └── No FK relationship to TokenBlacklist (linked by jti claim
      embedded in the JWT, not by user_id)
```

## JWT Token Structure

### Access Token Claims

| Claim | Type | Description |
|-------|------|-------------|
| sub | String | User ID (as string) |
| username | String | Username for display |
| type | String | "access" |
| jti | String | Unique token ID (UUID4) |
| exp | Integer | Expiration timestamp |
| iat | Integer | Issued-at timestamp |

### Refresh Token Claims

| Claim | Type | Description |
|-------|------|-------------|
| sub | String | User ID (as string) |
| type | String | "refresh" |
| jti | String | Unique token ID (UUID4) |
| exp | Integer | Expiration timestamp |
| iat | Integer | Issued-at timestamp |

## Configuration Variables (new in .env)

| Variable | Default | Description |
|----------|---------|-------------|
| JWT_SECRET_KEY | (required) | Secret key for HS256 signing |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Access token lifetime |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | 7 | Refresh token lifetime |
| ADMIN_USERNAME | admin | Initial admin username |
| ADMIN_PASSWORD | (required) | Initial admin password |
| ADMIN_EMAIL | admin@matchcombat.local | Initial admin email |
| SMTP_HOST | localhost | SMTP server host |
| SMTP_PORT | 587 | SMTP server port |
| SMTP_USER | (empty) | SMTP auth username |
| SMTP_PASSWORD | (empty) | SMTP auth password |
| SMTP_FROM_EMAIL | noreply@matchcombat.local | Sender email |
| SMTP_USE_TLS | True | Use STARTTLS |
| PASSWORD_RESET_EXPIRE_HOURS | 1 | Reset token lifetime |
