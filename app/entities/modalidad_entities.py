from pydantic import BaseModel

class ModalidadResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}