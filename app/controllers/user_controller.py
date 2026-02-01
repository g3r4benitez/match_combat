from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.security.deps import get_current_user
from app.entities.user_entities import UserCreateDTO, UserUpdateDTO, UserResponse
from app.models.user import User
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def list_users(session: Session = Depends(get_session)):
    return user_service.get_all_users(session)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return user_service.get_user_by_id(user_id, session)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateDTO,
    session: Session = Depends(get_session),
):
    return user_service.create_user(user_data, session)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdateDTO,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return user_service.update_user(user_id, user_data, session, current_user)
