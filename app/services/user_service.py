from sqlmodel import Session, select

from app.core.security.providers import get_password_hash
from app.entities.user_entities import UserCreateDTO, UserUpdateDTO, UserResponse
from app.exceptions.general_exeptions import (
    ConflictExeption,
    BadRequestException,
)
from app.models.user import User


def create_user(user_data: UserCreateDTO, session: Session) -> UserResponse:
    existing = session.exec(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    ).first()
    if existing:
        raise ConflictExeption(message="Username or email already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        nombre=user_data.nombre,
        apellido=user_data.apellido,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)


def get_all_users(session: Session) -> list[UserResponse]:
    users = session.exec(select(User)).all()
    return [UserResponse.model_validate(u) for u in users]


def get_user_by_id(user_id: int, session: Session) -> UserResponse:
    user = session.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


def update_user(
    user_id: int,
    user_data: UserUpdateDTO,
    session: Session,
    current_user: User | None = None,
) -> UserResponse:
    user = session.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != user.email:
        existing = session.exec(
            select(User).where(User.email == update_data["email"])
        ).first()
        if existing:
            raise ConflictExeption(message="Email already in use")

    if "is_active" in update_data and update_data["is_active"] is False:
        if current_user and current_user.id == user_id:
            active_count = len(
                session.exec(select(User).where(User.is_active == True)).all()
            )
            if active_count <= 1:
                raise BadRequestException(
                    message="Cannot deactivate the last active administrator"
                )

    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)
