import uuid as uuid_lib
from typing import Optional

from sqlmodel import Field, SQLModel


class Entrada(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    escuela: str
    usada: int = Field(default=0)
    uuid: str = Field(default_factory=lambda: str(uuid_lib.uuid4()), unique=True)
