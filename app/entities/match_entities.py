from sqlmodel import SQLModel

class MatchCreate(SQLModel):
    competidor_1_id: int
    competidor_2_id: int
    modalidad_id: int
    resultado: str