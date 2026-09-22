from sqlmodel import Session, select
from typing import List
from app.models.competidor import Modalidad
from app.core.database import engine
from app.entities.modalidad_entities import ModalidadResponse


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

    def get_modalidades(self) -> List[ModalidadResponse]:
        statement = select(Modalidad)
        modalidades = self.session.exec(statement).all()
        #
        return [ModalidadResponse.model_validate(m) for m in modalidades]



session = Session(engine)
modalidad_service = ModalidadService(session)