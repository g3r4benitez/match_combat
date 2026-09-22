from fastapi import HTTPException
from sqlmodel import Session, select

from app.entities.evento_entities import EventoCreateDTO, EventoUpdateDTO
from app.models.evento import Evento


class EventoService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Evento]:
        statement = select(Evento)
        results = self.session.exec(statement)
        return results.all()

    def get_by_id(self, evento_id: int) -> Evento:
        evento = self.session.get(Evento, evento_id)
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return evento

    def create(self, dto: EventoCreateDTO) -> Evento:
        evento = Evento(nombre=dto.nombre, fecha=dto.fecha, activo=dto.activo)
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def update(self, evento_id: int, dto: EventoUpdateDTO) -> Evento:
        evento = self.get_by_id(evento_id)
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(evento, key, value)
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def delete(self, evento_id: int) -> dict:
        evento = self.get_by_id(evento_id)
        self.session.delete(evento)
        self.session.commit()
        return {"detail": "Evento eliminado exitosamente"}
