import os

from starlette.config import Config

ROOT_DIR = os.getcwd()
_config = Config(os.path.join(ROOT_DIR, ".env"))
APP_VERSION = "0.0.1"
APP_NAME = "MATCH COMBAT"
API_PREFIX = ""

# Env vars
IS_DEBUG: bool = _config("IS_DEBUG", cast=bool, default=False)


DB_USER: str = _config("DB_USER", cast=str, default="match_user")
DB_PASSWORD: str = _config("DB_PASSWORD", cast=str, default="match_password")
DB_NAME: str = _config("DB_NAME", cast=str, default="match_combat")
DB_HOST: str = _config("DB_HOST", cast=str, default="localhost")
DB_PORT: str = _config("DB_PORT", cast=str, default="5432")

CHANNELS: str = "sms,email,push"
NOMBRE_EVENTO: str = _config("NOMBRE_EVENTO", cast=str, default="Match Combat")    

def get_database_url():
    """Generate the database url from the environment."""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DB_URL: str = get_database_url()


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
