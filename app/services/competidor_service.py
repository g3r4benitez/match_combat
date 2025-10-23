import csv
import io

from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from fastapi import HTTPException

from app.core.logger import logger
from app.models.criterios import CriteriosDTO
from app.models.competidor import Competidor, Match
from app.core.database import engine

modalidades = {
    1: "Kick Exhibicion",
    2:"Kick Amateur",
    3:"Box Exhibicion",
    4:"Box Amateur",
    5: "Full Exhibicion",
    6: "Full Amateur",
    7: "Muay Thai Exhibicion",
    8: "Muay Thai Amateur",
}


def export_all_competitors_to_csv(session: Session):
        """On this function I want to export the list of competidores to csv"""
        statement = (select(Competidor)
                    .order_by(Competidor.escuela))
        results = session.exec(statement)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['#', 'Nombre', 'Edad', 'Peso', 'Modalidad', 'Sexo', 'tiene_oponente?', 'Escuela', 'historial', 'Comentarios' ])

        for competidor in results:
            writer.writerow([
                competidor.id,
                competidor.nombre,
                competidor.edad,
                competidor.peso,
                modalidades[competidor.modalidad_id],
                'M' if competidor.sexo_id else 'F',
                'Si' if competidor.matched else 'No',
                competidor.escuela,
                competidor.historial_str,
                competidor.comentarios
            ])

        output.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="competidores.csv"'
        }
        return StreamingResponse(output, media_type='text/csv', headers=headers)

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
        logger.info("competidores listado")
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

        if not criterios.include_matched:
            statement = statement.where(Competidor.matched == False)
        
        if not criterios.include_others:
            statement = statement.where(Competidor.modalidad_id == criterios.modalidad_id)

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
    
    def delete(self, competidor_id: int, session: Session):
        competidor = session.get(Competidor, competidor_id)
        if not competidor:
            raise HTTPException(status_code=404, detail=f'Competidor con id {competidor_id} no encontrado')

        try:
            session.delete(competidor)
            session.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"No se pudo eliminar el match por que: '{e}'")

        return {"detail": "Competidor eliminado exitosamente"}


session = Session(engine)
competidor_service = CompetidorService(session)