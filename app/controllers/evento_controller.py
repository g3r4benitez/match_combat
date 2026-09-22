from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.entities.evento_entities import EventoCreateDTO, EventoUpdateDTO
from app.models.evento import Evento
from app.services.evento_service import EventoService

router = APIRouter()


@router.get("/", response_model=list[Evento])
def get_eventos(session: Session = Depends(get_session)):
    service = EventoService(session)
    return service.get_all()


@router.get("/{id}", response_model=Evento)
def get_evento_by_id(id: int, session: Session = Depends(get_session)):
    service = EventoService(session)
    return service.get_by_id(id)


@router.post("/", response_model=Evento)
def create_evento(dto: EventoCreateDTO, session: Session = Depends(get_session)):
    service = EventoService(session)
    return service.create(dto)


@router.put("/{id}", response_model=Evento)
def update_evento(id: int, dto: EventoUpdateDTO, session: Session = Depends(get_session)):
    service = EventoService(session)
    return service.update(id, dto)


@router.delete("/{id}")
def delete_evento(id: int, session: Session = Depends(get_session)):
    service = EventoService(session)
    return service.delete(id)
