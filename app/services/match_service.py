import csv
import io
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.competidor import Competidor
from app.entities.match_entities import MatchCreateDTO
from app.models.competidor import Match

def registrar_match(session: Session, match_data: MatchCreateDTO):
    # Validar que los competidores existen
    competidor_1 = session.get(Competidor, match_data.competidor_1_id)
    competidor_2 = session.get(Competidor, match_data.competidor_2_id)

    if not competidor_1 or not competidor_2:
        raise HTTPException(status_code=404, detail="Uno o ambos competidores no existen")

    # Crear el Match
    nuevo_match = Match(
        competidor_1_id=match_data.competidor_1_id,
        competidor_2_id=match_data.competidor_2_id,
        modalidad_id=match_data.modalidad_id,
        resultado=match_data.resultado,
    )

    try:
        competidor_1.matched = True
        competidor_2.matched = True
        session.add(competidor_1)
        session.add(competidor_2)
        session.add(nuevo_match)
        session.commit()
        session.refresh(nuevo_match)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo crear el match por que: '{e}'")

    return nuevo_match

def get_all_matchs(session: Session):
    statement = (select(Match))
    results = session.exec(statement)
    matchs = []
    for r in results:
        matchs.append({
            'competidor_1: ': r.competidor_1,
            'competidor_2: ': r.competidor_2,
        })
    return matchs

def export_all_matchs_to_csv(session: Session):
    """On this function I want to export the list of matchs to csv"""
    statement = select(Match)
    results = session.exec(statement)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'Peleador 1', 'Escuela', 'Peleador 2', 'Escuela', 'modalidad_id'])

    for match in results:
        writer.writerow([
            match.id,
            match.competidor_1.nombre,
            match.competidor_1.escuela, 
            match.competidor_2.nombre,
            match.competidor_2.escuela,
            match.modalidad.name,
        ])

    output.seek(0)
    return output.getvalue()


def get_matchs_by_modalidad_id(modalidad_id: int, session: Session):
    statement = (select(Match)
                 .where(Match.modalidad_id == modalidad_id))
    results = session.exec(statement)
    matchs = []
    for r in results:
        matchs.append({
            'competidor_1: ': r.competidor_1,
            'competidor_2: ': r.competidor_2,
        })
    return matchs