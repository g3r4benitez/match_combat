from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.database import get_session
from app.core.security.deps import get_current_user, oauth2_scheme
from app.entities.auth_entities import (
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    return auth_service.login(form_data.username, form_data.password, session)


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return auth_service.logout(token, session)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    body: RefreshTokenRequest,
    session: Session = Depends(get_session),
):
    return auth_service.refresh(body.refresh_token, session)


@router.post("/password-reset/request")
def request_password_reset(
    body: PasswordResetRequest,
    session: Session = Depends(get_session),
):
    return auth_service.request_password_reset(body.email, session)


@router.post("/password-reset/confirm")
def confirm_password_reset(
    body: PasswordResetConfirm,
    session: Session = Depends(get_session),
):
    return auth_service.confirm_password_reset(body.token, body.new_password, session)
