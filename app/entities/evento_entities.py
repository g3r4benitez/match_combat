from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class EventoCreateDTO(BaseModel):
    nombre: str
    fecha: date
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip()


class EventoUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    fecha: Optional[date] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip() if v is not None else v
