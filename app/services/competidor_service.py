from sqlmodel import Session, select

from app.core.logger import logger
from app.models.criterios import CriteriosDTO
from app.models.competidor import Competidor, Match
from app.core.database import engine


class CompetidorService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, competidor_id: int):
        return self.session.get(Competidor, competidor_id)

    def get_all(self, without_match: bool = False):
        statement = select(Competidor)
        if without_match == True:
            statement = statement.where(Competidor.matched == False)
        results = self.session.exec(statement)
        return results.all()

    def create_competidor(self, competidor: Competidor) -> Competidor:
        if competidor.id == 0:
            competidor.id = None

        self.session.add(competidor)
        self.session.commit()
        self.session.refresh(competidor)
        return competidor



    def get_match(self, criterios: CriteriosDTO):
        competidor = self.get(criterios.competidor_id)
        statement = (select(Competidor)
                     .where(Competidor.id != criterios.competidor_id)
                     .where(Competidor.sexo_id == competidor.sexo_id))
        

        print(criterios.include_matched, criterios.include_others)

        if not criterios.include_others:
            statement = statement.where(Competidor.modalidad_id == criterios.modalidad_id)

        if not criterios.include_matched:
            statement = statement.where(Competidor.matched == False)

        if criterios.edad_margen:
            edad_minima = competidor.edad - criterios.edad_margen
            edad_maxima = competidor.edad + criterios.edad_margen
            statement = statement.where(
                Competidor.edad.between(edad_minima, edad_maxima)
            )

        if criterios.peso_margen:
            logger.info(f"incluir en la busqueda criterio peso: {criterios.peso_margen}")
            peso_minimo = competidor.peso - criterios.peso_margen
            peso_maximo = competidor.peso + criterios.peso_margen
            statement = statement.where(
                Competidor.peso.between(peso_minimo, peso_maximo)
            )

        results = self.session.exec(statement)
        return results.all()

session = Session(engine)
competidor_service = CompetidorService(session)