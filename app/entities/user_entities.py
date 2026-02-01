from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    username: str
    password: str
    email: str
    nombre: str
    apellido: str


class UserUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nombre: str
    apellido: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
