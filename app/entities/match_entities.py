from pydantic import BaseModel
from typing import Optional


class MatchCreateDTO(BaseModel):
    competidor_1_id: int
    competidor_2_id: int
    modalidad_id: int
    resultado: Optional[str] = None
    comentarios: Optional[str] = None
    completada: Optional[bool] = False

class SortData(BaseModel):
    match_id: int
    orden: int


class MatchUpdateDTO(BaseModel):
    competidor_1_id: Optional[int] = None
    competidor_2_id: Optional[int] = None
    modalidad_id: Optional[int] = None
    resultado: Optional[str] = None
    comentarios: Optional[str] = None
    orden: Optional[int] = None
    completada: Optional[bool] = None



