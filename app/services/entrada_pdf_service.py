import logging
from io import BytesIO
from pathlib import Path

import boto3
import segno
from botocore.exceptions import ClientError
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.core.config import AWS_REGION, NOMBRE_EVENTO, ROOT_DIR, S3_SPONSORS_BUCKET
from app.models.entrada import Entrada

logger = logging.getLogger(__name__)

PAGE_WIDTH = 5 * cm
PAGE_HEIGHT = 10 * cm
MARGIN = 0.3 * cm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
LOCAL_SPONSORS_PATH = Path(ROOT_DIR) / "static" / "images" / "sponsors.png"


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

    def _load_sponsors_image(self) -> BytesIO | None:
        if S3_SPONSORS_BUCKET:
            try:
                s3 = boto3.client("s3", region_name=AWS_REGION)
                response = s3.get_object(Bucket=S3_SPONSORS_BUCKET, Key="sponsors.png")
                buf = BytesIO(response["Body"].read())
                buf.seek(0)
                return buf
            except ClientError as e:
                logger.warning("Failed to download sponsors.png from S3: %s", e)
        if LOCAL_SPONSORS_PATH.exists():
            return BytesIO(LOCAL_SPONSORS_PATH.read_bytes())
        logger.warning("No sponsors.png found in S3 or local filesystem")
        return None

    def _draw_sponsors_footer(self, c: canvas.Canvas) -> float:
        try:
            img_data = self._load_sponsors_image()
            if img_data is None:
                return 0.0
            img = ImageReader(img_data)
            iw, ih = img.getSize()
            img_width = CONTENT_WIDTH
            img_height = CONTENT_WIDTH * (ih / iw)
            x = (PAGE_WIDTH - img_width) / 2
            y = MARGIN
            c.drawImage(img, x, y, width=img_width, height=img_height)
            return img_height
        except (OSError, ValueError, SyntaxError):
            logger.warning("No se pudo cargar la imagen de sponsors")
            return 0.0

    def _fit_text(self, c: canvas.Canvas, text: str, font: str, size: float) -> str:
        max_width = CONTENT_WIDTH
        if c.stringWidth(text, font, size) <= max_width:
            return text
        while len(text) > 3 and c.stringWidth(text + "...", font, size) > max_width:
            text = text[:-1]
        return text + "..."
