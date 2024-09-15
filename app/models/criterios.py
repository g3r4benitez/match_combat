from sqlmodel import SQLModel

class CriteriosDTO(SQLModel):
    competidor_id: int
    edad_margen: int | None
    peso_margen: int | None
    modalidad_id: int
    historial_margen: int | None
    include_matched: bool = False