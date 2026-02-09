from typing import Optional

from pydantic import BaseModel, field_validator


class EntradaCreateDTO(BaseModel):
    nombre: str
    escuela: str

    @field_validator("nombre", "escuela")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip()


class EntradaUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    escuela: Optional[str] = None
    usada: Optional[int] = None

    @field_validator("nombre", "escuela")
    @classmethod
    def not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip() if v is not None else v

    @field_validator("usada")
    @classmethod
    def valid_usada(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (0, 1):
            raise ValueError("El campo usada solo acepta 0 (pendiente) o 1 (usada)")
        return v
