# Quickstart: JWT Authentication & Authorization

## Prerequisites

- Python 3.11+
- PostgreSQL running (or SQLite for local dev)
- SMTP server access (for password recovery)

## 1. Install new dependencies

```bash
pip install "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
```

Or add to requirements.txt and run:

```bash
pip install -r requirements.txt
```

## 2. Configure environment variables

Add to your `.env` file:

```env
# JWT Configuration
JWT_SECRET_KEY="your-secret-key-change-in-production"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Initial Admin (used only on first startup if no users exist)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
ADMIN_EMAIL=admin@matchcombat.local

# SMTP (for password recovery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@matchcombat.local
SMTP_USE_TLS=True
PASSWORD_RESET_EXPIRE_HOURS=1
```

## 3. Start the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

On first startup, the system will:
1. Create the User, TokenBlacklist, and PasswordResetToken tables
2. Seed an initial admin account using ADMIN_* env vars
3. Log a message confirming the admin was created

## 4. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=changeme123"
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

## 5. Access protected endpoints

```bash
# Use the access_token from login response
TOKEN="eyJ..."

# List competitors (now requires auth)
curl http://localhost:8000/api/competidor/ \
  -H "Authorization: Bearer $TOKEN"

# Search for matches (now requires auth)
curl -X POST http://localhost:8000/api/match/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"competidor_id": 1, "modalidad_id": 1, "edad_margen": 2, "peso_margen": 3}'
```

## 6. Create a new user

```bash
curl -X POST http://localhost:8000/api/user/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "coach1",
    "password": "securepass123",
    "email": "coach@gym.com",
    "nombre": "Juan",
    "apellido": "Perez"
  }'
```

## 7. Refresh token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

## 8. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

## 9. Password recovery

```bash
# Request reset
curl -X POST http://localhost:8000/api/auth/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@matchcombat.local"}'

# Confirm reset (use token from email)
curl -X POST http://localhost:8000/api/auth/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{"token": "reset-token-from-email", "new_password": "newpassword123"}'
```

## Verification checklist

- [ ] `GET /api/ping` returns "pong" without auth
- [ ] `GET /api/competidor/` returns 401 without token
- [ ] `POST /api/auth/login` returns tokens with valid credentials
- [ ] `GET /api/competidor/` returns data with valid token
- [ ] `POST /api/auth/logout` invalidates the token
- [ ] `GET /api/competidor/` returns 401 with invalidated token
- [ ] `POST /api/user/` creates a new user
- [ ] New user can login with their credentials
- [ ] 5 failed logins lock the account
