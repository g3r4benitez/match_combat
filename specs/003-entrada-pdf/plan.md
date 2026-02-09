# Implementation Plan: Generación de PDF de Entrada con QR

**Branch**: `003-entrada-pdf` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-entrada-pdf/spec.md`

## Summary

Crear un endpoint que genera un PDF descargable tipo boleto/ticket para una entrada existente. El PDF tiene formato vertical de 5x12 cm y contiene: encabezado "Titulo Evento" (temporal), nombre del titular, escuela, y un código QR con el UUID de la entrada. Se utilizarán reportlab para la generación del PDF y segno para la generación del código QR. Ambas librerías son nuevas dependencias del proyecto.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.112.0, SQLModel 0.0.22, reportlab >=4.0 (nuevo), segno >=1.6 (nuevo)
**Storage**: PostgreSQL (producción), SQLite (desarrollo) - sin cambios, no se persisten PDFs
**Testing**: pytest con httpx para testing de endpoints
**Target Platform**: Linux server
**Project Type**: single (backend API)
**Performance Goals**: Generación de PDF en menos de 5 segundos por solicitud
**Constraints**: PDF generado en memoria (BytesIO), sin almacenamiento en disco
**Scale/Scope**: Una solicitud de PDF a la vez (sin batch), endpoint individual

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | Endpoint RESTful GET /api/entradas/{id}/pdf, sigue convención de prefijo existente. Controller delega a service. |
| II. Domain Integrity | PASS | No afecta el dominio de matching. Solo lectura de la entidad Entrada. |
| III. Layered Architecture | PASS | Controller → Service (PDF generation). No se necesita repository nuevo, usa servicio existente de entradas para obtener datos. |
| IV. Data Consistency | PASS | Operación de solo lectura. No hay mutaciones de estado. |
| V. Simplicity and YAGNI | PASS | Solo se implementa lo solicitado: un endpoint, un servicio de PDF. Sin abstracciones innecesarias. Las dependencias nuevas (reportlab, segno) están justificadas por el requerimiento. |

### Post-Design Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. API-First Design | PASS | Contrato OpenAPI definido en contracts/entrada-pdf-api.yaml. DTO no requerido ya que la respuesta es un archivo binario (PDF). |
| II. Domain Integrity | PASS | Sin impacto en dominio de matching. |
| III. Layered Architecture | PASS | entrada_pdf_controller.py → entrada_pdf_service.py → servicio de entradas existente. |
| IV. Data Consistency | PASS | Solo lectura. |
| V. Simplicity and YAGNI | PASS | Dos archivos nuevos, dos dependencias nuevas. Sin over-engineering. |

## Project Structure

### Documentation (this feature)

```text
specs/003-entrada-pdf/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Library research
├── data-model.md        # Phase 1: Data model (references existing Entrada)
├── quickstart.md        # Phase 1: Quick implementation guide
├── contracts/           # Phase 1: API contracts
│   └── entrada-pdf-api.yaml
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
app/
├── controllers/
│   └── entrada_pdf_controller.py   # NEW - Endpoint GET /api/entradas/{id}/pdf
├── services/
│   └── entrada_pdf_service.py      # NEW - PDF generation logic with QR
├── api/routes/
│   └── router.py                   # MODIFIED - Register new router
└── ...                             # Existing files unchanged
```

**Structure Decision**: Sigue la estructura existente del proyecto. Se agregan dos archivos nuevos siguiendo el patrón Controller → Service. Se modifica router.py para registrar el nuevo endpoint.

## Complexity Tracking

> No violations detected. All constitution gates pass without exceptions.
