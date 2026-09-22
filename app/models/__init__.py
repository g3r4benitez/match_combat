"""SQLModel model registry and naming convention.

This module MUST be imported before any model class is defined elsewhere,
because it attaches a naming convention to SQLModel's shared MetaData object.

The naming convention is critical for SQLite batch mode: SQLModel's
``Field(foreign_key=...)`` produces unnamed constraints by default, and Alembic's
batch "move and copy" workflow cannot reflect or drop unnamed constraints on
SQLite. A deterministic naming convention ensures all FKs, PKs, indexes, and
checks get predictable names so batch migrations work correctly.
"""
from sqlalchemy.schema import MetaData
from sqlmodel import SQLModel

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Replace SQLModel's default MetaData with one that has a naming convention.
# Must happen BEFORE any model is imported so all tables register on this MetaData.
SQLModel.metadata = MetaData(naming_convention=convention)

# Import all table models so they register on the (now convention-bearing)
# SQLModel.metadata. This makes the full schema visible to Alembic autogenerate.
# These are intentional side-effect imports (models register themselves on
# SQLModel.metadata at class-definition time).
from app.models.area import Area  # noqa: F401
from app.models.competidor import Competidor, Match, Modalidad, Sexo  # noqa: F401
from app.models.entrada import Entrada  # noqa: F401
from app.models.evento import Evento  # noqa: F401
from app.models.user import PasswordResetToken, TokenBlacklist, User  # noqa: F401
