from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.entities.entrada_entities import EntradaCreateDTO, EntradaUpdateDTO
from app.models.entrada import Entrada
from app.services.entrada_service import EntradaService

router = APIRouter()


@router.get("/", response_model=list[Entrada])
def get_entradas(session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.get_all()


@router.get("/uuid/{uuid}", response_model=Entrada)
def get_entrada_by_uuid(uuid: str, session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.get_by_uuid(uuid)


@router.get("/{id}", response_model=Entrada)
def get_entrada_by_id(id: int, session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.get_by_id(id)


@router.post("/", response_model=Entrada)
def create_entrada(dto: EntradaCreateDTO, session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.create(dto)


@router.put("/{id}", response_model=Entrada)
def update_entrada(id: int, dto: EntradaUpdateDTO, session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.update(id, dto)


@router.delete("/{id}")
def delete_entrada(id: int, session: Session = Depends(get_session)):
    service = EntradaService(session)
    return service.delete(id)
