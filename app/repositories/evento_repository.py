from app.models.evento import Evento
from app.repositories.base_respository import BaseRepository


class EventoRepository(BaseRepository):
    model_name = Evento


evento_repository = EventoRepository()
