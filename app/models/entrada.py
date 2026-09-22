import uuid as uuid_lib
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.evento import Evento


class Entrada(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    escuela: str
    usada: int = Field(default=0)
    uuid: str = Field(default_factory=lambda: str(uuid_lib.uuid4()), unique=True)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")
    evento: Optional["Evento"] = Relationship(back_populates="entradas")
