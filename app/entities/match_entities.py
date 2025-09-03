from pydantic import BaseModel
from typing import Optional


class MatchCreateDTO(BaseModel):
    competidor_1_id: int
    competidor_2_id: int
    modalidad_id: int
    resultado: Optional[str] = None
    comentarios: Optional[str] = None


class MatchUpdateDTO(BaseModel):
    competidor_1_id: Optional[int] = None
    competidor_2_id: Optional[int] = None
    modalidad_id: Optional[int] = None
    resultado: Optional[str] = None
    comentarios: Optional[str] = None



