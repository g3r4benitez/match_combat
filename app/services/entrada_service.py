from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.entrada import Entrada
from app.entities.entrada_entities import EntradaCreateDTO, EntradaUpdateDTO


class EntradaService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Entrada]:
        statement = select(Entrada)
        results = self.session.exec(statement)
        return results.all()

    def get_by_id(self, entrada_id: int) -> Entrada:
        entrada = self.session.get(Entrada, entrada_id)
        if not entrada:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        return entrada

    def get_by_uuid(self, uuid: str) -> Entrada:
        statement = select(Entrada).where(Entrada.uuid == uuid)
        entrada = self.session.exec(statement).first()
        if not entrada:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        return entrada

    def create(self, dto: EntradaCreateDTO) -> Entrada:
        entrada = Entrada(nombre=dto.nombre, escuela=dto.escuela)
        self.session.add(entrada)
        self.session.commit()
        self.session.refresh(entrada)
        return entrada

    def update(self, entrada_id: int, dto: EntradaUpdateDTO) -> Entrada:
        entrada = self.get_by_id(entrada_id)
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entrada, key, value)
        self.session.add(entrada)
        self.session.commit()
        self.session.refresh(entrada)
        return entrada

    def delete(self, entrada_id: int) -> dict:
        entrada = self.get_by_id(entrada_id)
        self.session.delete(entrada)
        self.session.commit()
        return {"detail": "Entrada eliminada exitosamente"}
