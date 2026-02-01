from fastapi import APIRouter, Depends

from app.controllers import competidor_controller as competidor
from app.controllers import modalidad_controller as modalidad
from app.controllers import match_controller as match
from app.controllers import ping_controller as ping
from app.controllers import auth_controller as auth
from app.controllers import user_controller as user
from app.core.config import API_PREFIX
from app.core.security.deps import get_current_user

api_router = APIRouter(prefix=API_PREFIX)

api_router.include_router(
    competidor.router,
    tags=["competidor"],
    prefix="/api/competidor",
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    modalidad.router,
    tags=["modalidad"],
    prefix="/api/modalidad",
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    match.router,
    tags=["match"],
    prefix="/api/match",
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    ping.router,
    tags=["ping"],
    prefix="/api/ping",
)
api_router.include_router(
    auth.router,
    tags=["auth"],
    prefix="/api/auth",
)
api_router.include_router(
    user.router,
    tags=["user"],
    prefix="/api/user",
    dependencies=[Depends(get_current_user)],
)
