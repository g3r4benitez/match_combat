import os

from starlette.config import Config

ROOT_DIR = os.getcwd()
_config = Config(os.path.join(ROOT_DIR, ".env"))
APP_VERSION = "0.0.1"
APP_NAME = "MATCH COMBAT"
API_PREFIX = ""

# Env vars
IS_DEBUG: bool = _config("IS_DEBUG", cast=bool, default=False)

DB_URL: str = _config("DB_URL", cast=str, default="sqlite:///./app/sql_app.db")
CHANNELS: str = "sms,email,push"


def get_celery_broker_url():
    """Generate the broker url from the environment."""
    protocol = _config("CELERY_BROKER_PROTOCOL", cast=str, default="")
    username = _config("CELERY_BROKER_USERNAME", default="")
    password = _config("CELERY_BROKER_PASSWORD", cast=str, default="")
    host = _config("CELERY_BROKER_HOST", cast=str, default="")
    port = _config("CELERY_BROKER_PORT", cast=str, default="")
    db = _config("CELERY_BROKER_DB", cast=str, default="")
    return f"{protocol}://{username}:{password}@{host}:{port}/{db}"


# Celery
CELERY_BROKER_URL: str = get_celery_broker_url()

# JWT
JWT_SECRET_KEY: str = _config("JWT_SECRET_KEY", cast=str, default="change-this-secret-key-in-production")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = _config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = _config("JWT_REFRESH_TOKEN_EXPIRE_DAYS", cast=int, default=7)
JWT_ALGORITHM: str = "HS256"

# Initial Admin
ADMIN_USERNAME: str = _config("ADMIN_USERNAME", cast=str, default="admin")
ADMIN_PASSWORD: str = _config("ADMIN_PASSWORD", cast=str, default="changeme123")
ADMIN_EMAIL: str = _config("ADMIN_EMAIL", cast=str, default="admin@matchcombat.local")

# SMTP
SMTP_HOST: str = _config("SMTP_HOST", cast=str, default="localhost")
SMTP_PORT: int = _config("SMTP_PORT", cast=int, default=587)
SMTP_USER: str = _config("SMTP_USER", cast=str, default="")
SMTP_PASSWORD: str = _config("SMTP_PASSWORD", cast=str, default="")
SMTP_FROM_EMAIL: str = _config("SMTP_FROM_EMAIL", cast=str, default="noreply@matchcombat.local")
SMTP_USE_TLS: bool = _config("SMTP_USE_TLS", cast=bool, default=True)
PASSWORD_RESET_EXPIRE_HOURS: int = _config("PASSWORD_RESET_EXPIRE_HOURS", cast=int, default=1)
