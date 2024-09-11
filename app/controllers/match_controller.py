from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.services.competidor_service import CompetidorService
from app.core.database import get_session
from app.exceptions.general_exeptions import InternalServerError
from app.models.criterios import CriteriosDTO


router = APIRouter()

@router.post("/")
def search_oponents(criterios: CriteriosDTO,  session: Session = Depends(get_session)):
    competidor_service = CompetidorService(session)
    try:
        return competidor_service.get_match(criterios)
    except Exception as e:
        raise InternalServerError(message="Can't match")

