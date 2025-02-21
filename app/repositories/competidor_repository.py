from app.models.competidor import Competidor
from app.repositories.base_respository import BaseRepository

class CompetidorRepository(BaseRepository):
    model_name = Competidor


user_repository = CompetidorRepository()