from fastapi import HTTPException
from sqlmodel import Session, select

from app.entities.area_entities import AreaCreateDTO, AreaUpdateDTO
from app.models.area import Area
from app.models.evento import Evento


class AreaService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Area]:
        statement = select(Area)
        results = self.session.exec(statement)
        return results.all()

    def get_by_id(self, area_id: int) -> Area:
        area = self.session.get(Area, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area no encontrada")
        return area

    def get_by_evento(self, evento_id: int) -> list[Area]:
        evento = self.session.get(Evento, evento_id)
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        statement = select(Area).where(Area.evento_id == evento_id)
        results = self.session.exec(statement)
        return results.all()

    def _validate_evento(self, evento_id: int) -> None:
        evento = self.session.get(Evento, evento_id)
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

    def create(self, dto: AreaCreateDTO) -> Area:
        self._validate_evento(dto.evento_id)
        area = Area(nombre=dto.nombre, evento_id=dto.evento_id)
        self.session.add(area)
        self.session.commit()
        self.session.refresh(area)
        return area

    def update(self, area_id: int, dto: AreaUpdateDTO) -> Area:
        area = self.get_by_id(area_id)
        update_data = dto.model_dump(exclude_unset=True)
        if update_data.get("evento_id") is not None:
            self._validate_evento(update_data["evento_id"])
        for key, value in update_data.items():
            setattr(area, key, value)
        self.session.add(area)
        self.session.commit()
        self.session.refresh(area)
        return area

    def delete(self, area_id: int) -> dict:
        area = self.get_by_id(area_id)
        self.session.delete(area)
        self.session.commit()
        return {"detail": "Area eliminada exitosamente"}
