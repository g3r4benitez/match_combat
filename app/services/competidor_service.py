from sqlmodel import Session
from app.models.competidor import Competidor, Sexo
from app.core.database import engine


class CompetidorService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, competidor: Competidor) -> Competidor:
        if competidor.id == 0:
            competidor.id = None

        self.session.add(competidor)
        self.session.commit()
        self.session.refresh(competidor)
        return competidor


session = Session(engine)
user_service = CompetidorService(session)