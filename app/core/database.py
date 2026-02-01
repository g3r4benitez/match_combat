import os
from sqlmodel import create_engine, Session, SQLModel, select

from app.models.competidor import Competidor, Sexo, Modalidad
from app.models.user import User, TokenBlacklist, PasswordResetToken
from app.core.logger import logger

SQLALCHEMY_DATABASE_URL = os.environ.get("DB_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

def init_db():
    print("Executing init db")
    SQLModel.metadata.create_all(engine)

def seed_admin():
    from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL
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

def get_session():
    with Session(engine) as session:
        yield session
