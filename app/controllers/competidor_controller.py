from fastapi import APIRouter, Depends,UploadFile, File, HTTPException
from sqlmodel import Session, select
from typing import List
import pandas as pd
from io import StringIO

from app.models.competidor import Competidor
from app.services.competidor_service import CompetidorService
from app.core.database import get_session
from app.exceptions.general_exeptions import InternalServerError

router = APIRouter()

@router.get("")
def get_competidores(session: Session = Depends(get_session)):
    competidor_service = CompetidorService(session)
    try:
        return competidor_service.get_all()
    except Exception as e:
        raise InternalServerError(message=f"Can't get competidores: {e}")

@router.get("/sin_match")
def get_competidores_without_match(session: Session = Depends(get_session)):
    competidor_service = CompetidorService(session)
    try:
        return competidor_service.get_all(without_match=True)
    except Exception as e:
        raise InternalServerError(message=f"Can't get competidores: {e}")

@router.post("/", response_model=Competidor)
def create_user(competidor: Competidor, session: Session = Depends(get_session)):
    competidor_service = CompetidorService(session)
    try:
        return competidor_service.create_competidor(competidor)
    except Exception as e:
        raise InternalServerError(message="Can't create competidor")


@router.post("/importar_competidores/")
async def importar_competidores(file: UploadFile = File(...), session: Session = Depends(get_session)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

    # Leer el archivo CSV en un DataFrame de pandas
    content = await file.read()
    csv_data = StringIO(content.decode("utf-8"))
    df = pd.read_csv(csv_data)

    # Validar que el CSV tiene las columnas necesarias
    required_columns = {"edad", "peso", "modalidad_id", "sexo_id"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"El archivo CSV debe contener las columnas: {required_columns}")

    # Iniciar una sesión de base de datos
    # with Session(engine) as session:
    competidores = []

    # Iterar sobre cada fila del DataFrame y crear Competidor
    for _, row in df.iterrows():
        competidor = Competidor(
            nombre=row["nombre"],
            edad=row["edad"],
            peso=row["peso"],
            modalidad_id=row["modalidad_id"],
            sexo_id=row["sexo_id"],
            escuela=row["escuela"],
            historial=row['historial'],
            historial_str=row['historial_str'],
            comentarios=row['comentarios']
        )
        competidores.append(competidor)

    # Agregar los competidores a la sesión
    session.add_all(competidores)
    session.commit()

    return {"message": f"Se han importado {len(competidores)} competidores correctamente"}