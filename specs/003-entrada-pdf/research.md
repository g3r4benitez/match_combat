# Research: Generación de PDF de Entrada con QR

**Feature**: 003-entrada-pdf
**Date**: 2026-02-09

## R-001: PDF Generation Library

**Decision**: reportlab

**Rationale**: ReportLab es la librería más madura y mantenida para generación de PDFs en Python. Ofrece soporte nativo para tamaños de página personalizados mediante tuplas (e.g., `(5*cm, 12*cm)`), generación en memoria con BytesIO (ideal para FastAPI), y control preciso sobre posicionamiento de texto e imágenes. Es la opción más confiable para un formato compacto como 5x12 cm.

**Alternatives considered**:
- **fpdf2**: Más simple pero menor precisión en formatos pequeños personalizados.
- **weasyprint**: Basado en HTML/CSS, demasiado pesado para este caso de uso simple.
- **borb**: Menos maduro y menor comunidad.

## R-002: QR Code Generation Library

**Decision**: segno

**Rationale**: Segno es una librería de QR sin dependencias externas (pure Python), puede generar PNGs sin necesitar Pillow (tiene encoder PNG built-in), cumple con ISO/IEC 18004:2015(E), y supera a python-qrcode en rendimiento y features. API simple y directa para generar QR desde un string UUID.

**Alternatives considered**:
- **qrcode (python-qrcode)**: Requiere Pillow para salida PNG, más pesada en dependencias.
- **python-barcode**: No genera códigos QR, solo códigos de barras lineales.

## R-003: FastAPI PDF Response Pattern

**Decision**: Usar `StreamingResponse` con `BytesIO` y headers de content-disposition attachment.

**Rationale**: FastAPI soporta nativamente `StreamingResponse` para retornar archivos binarios. Ambas librerías (reportlab y segno) son síncronas, pero FastAPI ejecuta funciones síncronas en un threadpool automáticamente, por lo que no hay problemas de compatibilidad async.

**Key implementation notes**:
- ReportLab usa coordenadas con origen (0,0) en la esquina inferior izquierda.
- Siempre llamar `.seek(0)` en BytesIO después de escribir y antes de leer/retornar.
- Importar `cm` de `reportlab.lib.units` para trabajar con centímetros en lugar de puntos.
- Para el QR en PDF: generar el QR como PNG en BytesIO con segno, luego usar `drawImage` de ReportLab con `ImageReader` para embeber el QR en el PDF.

## R-004: Dependencias a agregar

| Librería | Versión | Tamaño aprox. |
|----------|---------|---------------|
| reportlab | >=4.0 | ~4-5 MB |
| segno | >=1.6 | <1 MB |

Nota: reportlab depende de Pillow, que se instalará automáticamente como subdependencia.
