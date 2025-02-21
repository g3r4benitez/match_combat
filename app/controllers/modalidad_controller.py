from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.competidor import Modalidad
from app.services.modalidad_service import ModalidadService
from app.core.database import get_session
from app.exceptions.general_exeptions import InternalServerError

router = APIRouter()

@router.post("/", response_model=Modalidad)
def create_modalidad(modalidad: Modalidad, session: Session = Depends(get_session)):
    modalidad_service = ModalidadService(session)
    try:
        return modalidad_service.create_modalidad(modalidad)
    except Exception as e:
        raise InternalServerError(message="Can't create modalidad")


@router.get("")
def get_modalidades(session: Session = Depends(get_session)):
    modalidad_service = ModalidadService(session)
    try:
        return modalidad_service.get_modalidades()
    except Exception as e:
        raise InternalServerError(message="Can't get modalidades")


