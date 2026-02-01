from datetime import datetime, timedelta

from jose import JWTError
from sqlmodel import Session, select

from app.core.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    PASSWORD_RESET_EXPIRE_HOURS,
)
from app.core.security.base import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.security.providers import verify_password, get_password_hash
from app.entities.auth_entities import (
    TokenResponse,
    RefreshTokenResponse,
)
from app.exceptions.authentication_exceptions import UnauthorizedException
from app.exceptions.general_exeptions import BadRequestException
from app.core.error_handler import HTTPCustomException
from app.models.user import User, TokenBlacklist, PasswordResetToken
from app.core.logger import logger

LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION_MINUTES = 15


def authenticate_user(username: str, password: str, session: Session) -> User:
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        raise UnauthorizedException(message="Invalid credentials")

    if not user.is_active:
        raise UnauthorizedException(message="Account is inactive")

    if (
        user.failed_login_attempts >= LOCKOUT_THRESHOLD
        and user.last_failed_login_at
        and (datetime.utcnow() - user.last_failed_login_at)
        < timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    ):
        raise HTTPCustomException(
            status_code=423,
            msg="Account locked. Try again later.",
            type_value="locked",
        )

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        user.last_failed_login_at = datetime.utcnow()
        session.add(user)
        session.commit()
        raise UnauthorizedException(message="Invalid credentials")

    user.failed_login_attempts = 0
    user.last_failed_login_at = None
    session.add(user)
    session.commit()
    return user


def login(username: str, password: str, session: Session) -> TokenResponse:
    user = authenticate_user(username, password, session)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def logout(token: str, session: Session) -> dict:
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException()

    jti = payload.get("jti")
    exp_timestamp = payload.get("exp")
    expires_at = datetime.utcfromtimestamp(exp_timestamp) if exp_timestamp else datetime.utcnow()

    blacklist_entry = TokenBlacklist(jti=jti, expires_at=expires_at)
    session.add(blacklist_entry)
    session.commit()
    return {"message": "Logout successful"}


def refresh(refresh_token_str: str, session: Session) -> RefreshTokenResponse:
    try:
        payload = decode_token(refresh_token_str)
    except JWTError:
        raise UnauthorizedException(message="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedException(message="Invalid refresh token")

    jti = payload.get("jti")
    if jti:
        blacklisted = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        ).first()
        if blacklisted:
            raise UnauthorizedException(message="Invalid refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="Invalid refresh token")

    user = session.get(User, int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException(message="Invalid refresh token")

    new_access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return RefreshTokenResponse(access_token=new_access_token)


def request_password_reset(email: str, session: Session) -> dict:
    import uuid

    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        token_value = str(uuid.uuid4())
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=user.id,
            expires_at=datetime.utcnow()
            + timedelta(hours=PASSWORD_RESET_EXPIRE_HOURS),
        )
        session.add(reset_token)
        session.commit()

        try:
            from app.services.email_service import send_password_reset_email
            send_password_reset_email(user.email, token_value)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")

    return {"message": "If the email exists, a reset link has been sent."}


def confirm_password_reset(token_value: str, new_password: str, session: Session) -> dict:
    reset_token = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token == token_value)
    ).first()

    if not reset_token:
        raise BadRequestException(message="Invalid or expired reset token")

    if reset_token.used:
        raise BadRequestException(message="Invalid or expired reset token")

    if reset_token.expires_at < datetime.utcnow():
        raise BadRequestException(message="Invalid or expired reset token")

    user = session.get(User, reset_token.user_id)
    if not user:
        raise BadRequestException(message="Invalid or expired reset token")

    user.hashed_password = get_password_hash(new_password)
    reset_token.used = True
    session.add(user)
    session.add(reset_token)
    session.commit()

    return {"message": "Password updated successfully"}


def cleanup_expired_tokens(session: Session) -> None:
    expired = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.expires_at < datetime.utcnow())
    ).all()
    for entry in expired:
        session.delete(entry)
    if expired:
        session.commit()
        logger.info(f"Cleaned up {len(expired)} expired blacklisted tokens")
