from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    failed_login_attempts: int = Field(default=0)
    last_failed_login_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    password_reset_tokens: List["PasswordResetToken"] = Relationship(
        back_populates="user"
    )


class TokenBlacklist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(max_length=255, unique=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="password_reset_tokens")
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
