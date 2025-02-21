from dependency_injector import containers, providers
from app.services.competidor_service import CompetidorService

class ContainerService(containers.DeclarativeContainer):
    sms_service = providers.Singleton( CompetidorService )
