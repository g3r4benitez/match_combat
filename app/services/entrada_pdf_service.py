import logging
from io import BytesIO
from pathlib import Path

import segno
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.models.entrada import Entrada
from app.core.config import NOMBRE_EVENTO, ROOT_DIR

logger = logging.getLogger(__name__)

PAGE_WIDTH = 5 * cm
PAGE_HEIGHT = 10 * cm
MARGIN = 0.3 * cm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
SPONSORS_IMAGE_PATH = Path(ROOT_DIR) / "static" / "images" / "sponsors.png"


class EntradaPdfService:

    def generate_pdf(self, entrada: Entrada) -> BytesIO:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

        y = PAGE_HEIGHT - MARGIN

        # Header: "Titulo Evento"
        c.setFont("Helvetica-Bold", 9)
        header = NOMBRE_EVENTO
        header_width = c.stringWidth(header, "Helvetica-Bold", 9)
        c.drawString((PAGE_WIDTH - header_width) / 2, y - 0.4 * cm, header)
        y -= 1.0 * cm

        # Separator line
        c.setStrokeColorRGB(0.3, 0.3, 0.3)
        c.setLineWidth(0.5)
        c.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
        y -= 0.5 * cm

        # Nombre
        c.setFont("Helvetica-Bold", 7)
        c.drawString(MARGIN, y, "Nombre:")
        y -= 0.4 * cm
        c.setFont("Helvetica", 7)
        nombre_text = self._fit_text(c, entrada.nombre, "Helvetica", 7)
        c.drawString(MARGIN, y, nombre_text)
        y -= 0.6 * cm

        # Escuela
        c.setFont("Helvetica-Bold", 7)
        c.drawString(MARGIN, y, "Escuela:")
        y -= 0.4 * cm
        c.setFont("Helvetica", 7)
        escuela_text = self._fit_text(c, entrada.escuela, "Helvetica", 7)
        c.drawString(MARGIN, y, escuela_text)
        y -= 0.8 * cm

        # Sponsors footer
        sponsors_height = self._draw_sponsors_footer(c)

        # QR Code
        qr_size = min(3.5 * cm, CONTENT_WIDTH)
        qr_x = (PAGE_WIDTH - qr_size) / 2
        qr_y = MARGIN + sponsors_height + 0.2 * cm

        qr_buffer = self._generate_qr(entrada.uuid)
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def _generate_qr(self, data: str) -> BytesIO:
        qr = segno.make_qr(data)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, kind="png", scale=10, border=1)
        qr_buffer.seek(0)
        return qr_buffer

    def _draw_sponsors_footer(self, c: canvas.Canvas) -> float:
        try:
            img = ImageReader(str(SPONSORS_IMAGE_PATH))
            iw, ih = img.getSize()
            img_width = CONTENT_WIDTH
            img_height = CONTENT_WIDTH * (ih / iw)
            x = (PAGE_WIDTH - img_width) / 2
            y = MARGIN
            c.drawImage(img, x, y, width=img_width, height=img_height)
            return img_height
        except Exception:
            logger.warning("No se pudo cargar la imagen de sponsors: %s", SPONSORS_IMAGE_PATH)
            return 0.0

    def _fit_text(self, c: canvas.Canvas, text: str, font: str, size: float) -> str:
        max_width = CONTENT_WIDTH
        if c.stringWidth(text, font, size) <= max_width:
            return text
        while len(text) > 3 and c.stringWidth(text + "...", font, size) > max_width:
            text = text[:-1]
        return text + "..."
