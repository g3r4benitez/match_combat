from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.core.database import get_session
from app.models.entrada import Entrada
from app.services.entrada_pdf_service import EntradaPdfService

router = APIRouter()


@router.get("/{id}/pdf")
def generate_entrada_pdf(id: int, session: Session = Depends(get_session)):
    entrada = session.get(Entrada, id)
    if not entrada:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")

    pdf_service = EntradaPdfService()
    pdf_buffer = pdf_service.generate_pdf(entrada)

    headers = {
        "Content-Disposition": f'attachment; filename="entrada-{id}.pdf"'
    }
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers,
    )
