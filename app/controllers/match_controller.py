from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.services.competidor_service import CompetidorService
from app.core.database import get_session
from app.models.criterios import CriteriosDTO
from app.models.competidor import Match
from app.entities.match_entities import MatchCreate
from app.services.match_service import registrar_match, get_matchs_by_modalidad_id, get_all_matchs, break_match


router = APIRouter()

@router.post("/")
def search_oponents(criterios: CriteriosDTO,  session: Session = Depends(get_session)):
    competidor_service = CompetidorService(session)
    #try:
    return competidor_service.get_match(criterios)
    #except Exception as e:
    #    raise InternalServerError(message=f"Can't get matchs, cause: '{e}'")

@router.post("/create/", response_model=Match)
def crear_match(match_data: MatchCreate, session: Session = Depends(get_session)):
    # Llama al servicio para registrar el partido
    return registrar_match(session, match_data)

@router.get("/")
def get_matchs(session: Session = Depends(get_session)):
    return get_all_matchs(session)

@router.get("/{modalidad_id}")
def get_matchs_by_modalidad(modalidad_id: int, session: Session = Depends(get_session)):
    return get_matchs_by_modalidad_id(modalidad_id, session)

@router.delete("/{match_id}")
def break_match(match_id: int, session: Session = Depends(get_session)):
    return break_match(session, match_id)
