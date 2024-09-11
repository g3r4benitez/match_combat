from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Sexo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    competidores: List["Competidor"] = Relationship(back_populates="sexo")

class Modalidad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    competidores: List["Competidor"] = Relationship(back_populates="modalidad")

class Competidor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    edad: int
    peso: float
    escuela: str
    modalidad_id: Optional[int] = Field(default=None, foreign_key="modalidad.id")
    modalidad: Optional[Modalidad] = Relationship(back_populates="competidores")
    sexo_id: Optional[int] = Field(default=None, foreign_key="sexo.id")
    sexo: Optional[Sexo] = Relationship(back_populates="competidores")
    matched: bool = Field(default=False)
    historial: int
    historial_str: str
