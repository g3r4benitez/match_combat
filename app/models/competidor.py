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
    matchs: List["Match"] = Relationship(back_populates="modalidad")

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
    comentarios: str

    matches_como_primero: List["Match"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Match.competidor_1_id==Competidor.id"}, back_populates="competidor_1")
    matches_como_segundo: List["Match"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Match.competidor_2_id==Competidor.id"}, back_populates="competidor_2")

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    competidor_1_id: int = Field(foreign_key="competidor.id")
    competidor_2_id: int = Field(foreign_key="competidor.id")

    competidor_1: Optional[Competidor] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Match.competidor_1_id==Competidor.id"},
        back_populates="matches_como_primero")
    competidor_2: Optional[Competidor] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Match.competidor_2_id==Competidor.id"},
        back_populates="matches_como_segundo")

    modalidad_id: Optional[int] = Field(default=None, foreign_key="modalidad.id")
    modalidad: Optional[Modalidad] = Relationship(back_populates="matchs")
