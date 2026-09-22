from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# Import ALL model modules so they register on SQLModel.metadata.
# This is critical: SQLModel uses a single shared MetaData object.
# Do NOT import CriteriosDTO (it is a DTO, not a table model).
# These imports are intentional side-effect imports for metadata registration.
from app.models.area import Area  # noqa: F401
from app.models.competidor import Competidor, Match, Modalidad, Sexo  # noqa: F401
from app.models.entrada import Entrada  # noqa: F401
from app.models.evento import Evento  # noqa: F401
from app.models.user import PasswordResetToken, TokenBlacklist, User  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to SQLModel's shared MetaData so autogenerate
# can detect all tables, columns, and constraints.
target_metadata = SQLModel.metadata


def get_url():
    """Read the database URL from the app's config module (single source of truth)."""
    from app.core.config import DB_URL
    return DB_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to
    the script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Enable batch mode only for SQLite — SQLite has limited ALTER TABLE
        # support, so Alembic performs a "move and copy" recreation.
        # This is safe for PostgreSQL since batch mode only activates for SQLite.
        use_batch = connection.dialect.name == "sqlite"

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=use_batch,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
