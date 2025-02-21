from sqlmodel import Session, select
from typing import List
from app.models.competidor import Modalidad
from app.core.database import engine


class ModalidadService:
    def __init__(self, session: Session):
        self.session = session

    def create_modalidad(self, modalidad: Modalidad) -> Modalidad:
        if modalidad.id == 0:
            modalidad.id = None

        self.session.add(modalidad)
        self.session.commit()
        self.session.refresh(modalidad)
        return modalidad

    def get_modalidades(self) -> List[Modalidad]:
        statement = select(Modalidad)
        results = self.session.exec(statement)
        return results.all()



session = Session(engine)
modalidad_service = ModalidadService(session)