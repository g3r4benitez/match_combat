from datetime import date
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.area import Area
from app.models.competidor import Competidor, Match, Modalidad
from app.models.entrada import Entrada


class Evento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    fecha: date
    activo: bool = Field(default=True)

    areas: List["Area"] = Relationship(back_populates="evento")
    modalidades: List["Modalidad"] = Relationship(back_populates="evento")
    competidores: List["Competidor"] = Relationship(back_populates="evento")
    matchs: List["Match"] = Relationship(back_populates="evento")
    entradas: List["Entrada"] = Relationship(back_populates="evento")
