from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlmodel import Session, create_engine, select

from app.core.config import DB_URL, SQL_ECHO
from app.core.logger import logger
from app.models.competidor import Sexo
from app.models.evento import Evento
from app.models.user import User


def create_db_engine(url: str):
    """Build the SQLAlchemy engine, enabling SQLite concurrency settings."""
    parsed_url = make_url(url)

    if parsed_url.get_backend_name() != "sqlite":
        return create_engine(url, echo=SQL_ECHO)

    database = parsed_url.database
    if database and database != ":memory:":
        Path(database).expanduser().parent.mkdir(parents=True, exist_ok=True)

    sqlite_engine = create_engine(
        url,
        echo=SQL_ECHO,
        connect_args={"timeout": 30, "check_same_thread": False},
    )

    @event.listens_for(sqlite_engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    return sqlite_engine


engine = create_db_engine(DB_URL)

def init_db():
    print("Executing init db")
    from alembic.config import Config

    from alembic import command

    alembic_cfg = Config(str(Path(__file__).resolve().parent.parent.parent / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed")
    print("init db ended")

def seed_admin():
    from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME
    from app.core.security.providers import get_password_hash

    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing:
            return
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            nombre="Admin",
            apellido="Admin",
        )
        session.add(admin)
        session.commit()
        logger.info(f"Initial admin user '{ADMIN_USERNAME}' created")

def seed_evento():
    from datetime import datetime, timezone

    from app.core.config import NOMBRE_EVENTO

    with Session(engine) as session:
        existing = session.exec(select(Evento)).first()
        if not existing:
            evento = Evento(nombre=NOMBRE_EVENTO, fecha=datetime.now(tz=timezone.utc).date(), activo=True)
            session.add(evento)
            session.commit()
            logger.info(f"Initial evento '{NOMBRE_EVENTO}' created")

    with Session(engine) as session:
        existing_sexos = session.exec(select(Sexo)).first()
        if not existing_sexos: 
            evento = Sexo(name="Masculino")
            session.add(evento)
            session.commit()

            evento = Sexo(name="Femenino")
            session.add(evento)
            session.commit()

            evento = Sexo(name="Otro")
            session.add(evento)
            session.commit()
            logger.info("Se crearon los sexos")

            

def get_session():
    with Session(engine) as session:
        yield session
