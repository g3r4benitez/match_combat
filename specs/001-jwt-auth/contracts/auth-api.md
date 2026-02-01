# API Contracts: JWT Authentication & Authorization

## Authentication Endpoints

### POST /api/auth/login

Login with username and password. Returns access and refresh tokens.

**Authentication**: None (public)

**Request Body** (application/x-www-form-urlencoded):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Account username |
| password | string | Yes | Account password |

Uses OAuth2PasswordRequestForm (FastAPI standard).

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Response 401** (invalid credentials):
```json
{
  "detail": [{"loc": [], "msg": "Invalid credentials", "type": "unauthorized"}]
}
```

**Response 423** (account locked):
```json
{
  "detail": [{"loc": [], "msg": "Account locked. Try again later.", "type": "locked"}]
}
```

---

### POST /api/auth/logout

Invalidate the current access token.

**Authentication**: Bearer token (required)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Response 200**:
```json
{
  "message": "Logout successful"
}
```

**Response 401** (invalid/missing token):
```json
{
  "detail": [{"loc": [], "msg": "Unauthorized", "type": "unauthorized"}]
}
```

---

### POST /api/auth/refresh

Issue a new access token using a valid refresh token.

**Authentication**: None (uses refresh token in body)

**Request Body** (application/json):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Yes | Valid refresh token |

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Response 401** (invalid/expired refresh token):
```json
{
  "detail": [{"loc": [], "msg": "Invalid refresh token", "type": "unauthorized"}]
}
```

---

### POST /api/auth/password-reset/request

Request a password reset email.

**Authentication**: None (public)

**Request Body** (application/json):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Registered email address |

**Response 200** (always, to prevent user enumeration):
```json
{
  "message": "If the email exists, a reset link has been sent."
}
```

---

### POST /api/auth/password-reset/confirm

Set a new password using a valid reset token.

**Authentication**: None (public, uses reset token)

**Request Body** (application/json):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Reset token from email |
| new_password | string | Yes | New password (min 8 chars) |

**Response 200**:
```json
{
  "message": "Password updated successfully"
}
```

**Response 400** (invalid/expired token):
```json
{
  "detail": [{"loc": [], "msg": "Invalid or expired reset token", "type": "bad_request"}]
}
```

---

## User Management Endpoints

### GET /api/user/

List all users (passwords excluded).

**Authentication**: Bearer token (required)

**Response 200**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@matchcombat.local",
    "nombre": "Admin",
    "apellido": "User",
    "is_active": true,
    "created_at": "2026-01-29T10:00:00"
  }
]
```

---

### GET /api/user/{user_id}

Get a single user by ID (password excluded).

**Authentication**: Bearer token (required)

**Response 200**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@matchcombat.local",
  "nombre": "Admin",
  "apellido": "User",
  "is_active": true,
  "created_at": "2026-01-29T10:00:00"
}
```

**Response 404**:
```json
{
  "detail": [{"loc": [], "msg": "User not found", "type": "not_found"}]
}
```

---

### POST /api/user/

Create a new user account.

**Authentication**: Bearer token (required)

**Request Body** (application/json):

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| username | string | Yes | 3-50 chars, unique |
| password | string | Yes | min 8 chars |
| email | string | Yes | valid email, unique |
| nombre | string | Yes | 1-100 chars |
| apellido | string | Yes | 1-100 chars |

**Response 201**:
```json
{
  "id": 2,
  "username": "new_admin",
  "email": "new@matchcombat.local",
  "nombre": "New",
  "apellido": "Admin",
  "is_active": true,
  "created_at": "2026-01-29T12:00:00"
}
```

**Response 409** (duplicate username or email):
```json
{
  "detail": [{"loc": [], "msg": "Username or email already exists", "type": "conflict"}]
}
```

---

### PATCH /api/user/{user_id}

Update user profile fields.

**Authentication**: Bearer token (required)

**Request Body** (application/json, all fields optional):

| Field | Type | Description |
|-------|------|-------------|
| nombre | string | Updated first name |
| apellido | string | Updated last name |
| email | string | Updated email (must be unique) |
| is_active | boolean | Activate/deactivate account |

**Response 200**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "updated@matchcombat.local",
  "nombre": "Updated",
  "apellido": "Name",
  "is_active": true,
  "created_at": "2026-01-29T10:00:00"
}
```

**Response 404**: User not found
**Response 409**: Email already in use

---

## Protected Existing Endpoints

All existing endpoints now require `Authorization: Bearer <token>`
header. The dependency is applied at the router level.

| Prefix | Protection |
|--------|------------|
| `/api/competidor` | Bearer token required |
| `/api/modalidad` | Bearer token required |
| `/api/match` | Bearer token required |
| `/api/ping` | Public (no token required) |
| `/api/auth/login` | Public |
| `/api/auth/refresh` | Public |
| `/api/auth/password-reset/*` | Public |
| `/api/auth/logout` | Bearer token required |
| `/api/user/*` | Bearer token required |

## Error Response Format

All error responses follow the existing project convention:

```json
{
  "detail": [
    {
      "loc": [],
      "msg": "Human-readable error message",
      "type": "error_type"
    }
  ]
}
```
