from fastapi import APIRouter

from app.controllers import competidor_controller as competidor
from app.controllers import ping_controller as ping
from app.core.config import API_PREFIX

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(competidor.router, tags=["competidor"], prefix="/api/competidor")
api_router.include_router(ping.router, tags=["ping"], prefix="/api/ping")


