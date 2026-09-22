from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.entities.area_entities import AreaCreateDTO, AreaUpdateDTO
from app.models.area import Area
from app.services.area_service import AreaService

router = APIRouter()


@router.get("/", response_model=list[Area])
def get_areas(session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.get_all()


@router.get("/evento/{evento_id}", response_model=list[Area])
def get_areas_by_evento(evento_id: int, session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.get_by_evento(evento_id)


@router.get("/{id}", response_model=Area)
def get_area_by_id(id: int, session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.get_by_id(id)


@router.post("/", response_model=Area)
def create_area(dto: AreaCreateDTO, session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.create(dto)


@router.put("/{id}", response_model=Area)
def update_area(id: int, dto: AreaUpdateDTO, session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.update(id, dto)


@router.delete("/{id}")
def delete_area(id: int, session: Session = Depends(get_session)):
    service = AreaService(session)
    return service.delete(id)
