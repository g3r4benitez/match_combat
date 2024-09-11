from fastapi import APIRouter

from app.controllers import competidor_controller as competidor
from app.controllers import modalidad_controller as modalidad
from app.controllers import match_controller as match
from app.controllers import ping_controller as ping
from app.core.config import API_PREFIX

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(competidor.router, tags=["competidor"], prefix="/api/competidor")
api_router.include_router(modalidad.router, tags=["modalidad"], prefix="/api/modalidad")
api_router.include_router(match.router, tags=["match"], prefix="/api/match")
api_router.include_router(ping.router, tags=["ping"], prefix="/api/ping")


