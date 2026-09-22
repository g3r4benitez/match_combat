from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.competidor import Match
    from app.models.evento import Evento


class Area(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    evento_id: int = Field(foreign_key="evento.id")
    evento: Optional["Evento"] = Relationship(back_populates="areas")
    matchs: List["Match"] = Relationship(back_populates="area")
