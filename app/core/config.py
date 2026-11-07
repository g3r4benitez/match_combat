import os

from starlette.config import Config

ROOT_DIR = os.getcwd()
_config = Config(os.path.join(ROOT_DIR, ".env"))
APP_VERSION = "0.0.1"
APP_NAME = "MATCH COMBAT"
API_PREFIX = ""

# Env vars
IS_DEBUG: bool = _config("IS_DEBUG", cast=bool, default=False)

# Database
# SQLite is the default engine. DB_URL can point to another file or an
# absolute path, e.g. sqlite:////var/lib/match_combat/match_combat.db
DB_URL: str = _config(
    "DB_URL",
    cast=str,
    default="sqlite:///data/match_combat.db",
)
SQL_ECHO: bool = _config("SQL_ECHO", cast=bool, default=False)

CHANNELS: str = "sms,email,push"
NOMBRE_EVENTO: str = _config("NOMBRE_EVENTO", cast=str, default="Match Combat")

# JWT
JWT_SECRET_KEY: str = _config("JWT_SECRET_KEY", cast=str, default="change-this-secret-key-in-production")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = _config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = _config("JWT_REFRESH_TOKEN_EXPIRE_DAYS", cast=int, default=7)
JWT_ALGORITHM: str = "HS256"
PASSWORD_RESET_EXPIRE_HOURS: int = _config("PASSWORD_RESET_EXPIRE_HOURS", cast=int, default=1)

# Initial Admin
ADMIN_USERNAME: str = _config("ADMIN_USERNAME", cast=str, default="admin")
ADMIN_PASSWORD: str = _config("ADMIN_PASSWORD", cast=str, default="changeme123")
ADMIN_EMAIL: str = _config("ADMIN_EMAIL", cast=str, default="admin@matchcombat.local")

# SMTP (optional - password reset emails)
SMTP_HOST: str = _config("SMTP_HOST", cast=str, default="")
SMTP_PORT: str = _config("SMTP_PORT", cast=str, default="")
SMTP_USER: str = _config("SMTP_USER", cast=str, default="")
SMTP_PASSWORD: str = _config("SMTP_PASSWORD", cast=str, default="")
SMTP_FROM_EMAIL: str = _config("SMTP_FROM_EMAIL", cast=str, default="")
SMTP_USE_TLS: bool = _config("SMTP_USE_TLS", cast=bool, default=True)

# S3 (sponsors PDF footer image)
AWS_REGION: str = _config("AWS_REGION", cast=str, default="us-east-1")
S3_SPONSORS_BUCKET: str = _config("S3_SPONSORS_BUCKET", cast=str, default="")
