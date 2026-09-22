from pathlib import Path

from sqlmodel import Session, create_engine, select

from app.core.config import DB_URL
from app.core.logger import logger
from app.models.evento import Evento
from app.models.user import User
from app.models.competidor import Sexo

engine = create_engine(DB_URL, echo=True)

def init_db():
    print("Executing init db")
    #from alembic.config import Config

    #from alembic import command

    #alembic_cfg = Config(str(Path(__file__).resolve().parent.parent.parent / "alembic.ini"))
    #command.upgrade(alembic_cfg, "head")

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
