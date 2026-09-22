from app.models.area import Area
from app.repositories.base_respository import BaseRepository


class AreaRepository(BaseRepository):
    model_name = Area


area_repository = AreaRepository()
