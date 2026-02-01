from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security.base import decode_token
from app.exceptions.authentication_exceptions import UnauthorizedException
from app.models.user import User, TokenBlacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException()

    if payload.get("type") != "access":
        raise UnauthorizedException()

    jti = payload.get("jti")
    if jti:
        blacklisted = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        ).first()
        if blacklisted:
            raise UnauthorizedException()

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException()

    user = session.get(User, int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException()

    return user
