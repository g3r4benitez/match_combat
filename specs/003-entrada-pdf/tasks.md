# Tasks: Generación de PDF de Entrada con QR

**Input**: Design documents from `/specs/003-entrada-pdf/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No tests explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `app/` at repository root (existing project structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install new dependencies required for PDF and QR generation

- [x] T001 Add reportlab and segno dependencies to requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks needed. This feature builds on existing infrastructure (Entrada model from 002-entradas-crud, JWT auth from 001-jwt-auth, database session management). All shared components already exist.

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Generar y descargar PDF de una entrada (Priority: P1) 🎯 MVP

**Goal**: Allow an admin to generate and download a PDF ticket for an existing entrada. The PDF is 5cm x 12cm portrait format, containing the event title header ("Titulo Evento"), the holder's name, school, and a QR code encoding the entrada's UUID.

**Independent Test**: Request PDF generation for an existing entrada, download the file, verify it contains correct information (header, name, school, QR with UUID) and has the correct dimensions.

### Implementation for User Story 1

- [x] T002 [P] [US1] Create PDF generation service with QR code embedding in app/services/entrada_pdf_service.py
  - Import reportlab (Canvas, cm units, ImageReader) and segno
  - Create class `EntradaPdfService` with method `generate_pdf(entrada)` that returns BytesIO
  - Set page size to `(5*cm, 12*cm)` portrait
  - Draw header text "Titulo Evento" centered at top
  - Draw "Nombre:" label and entrada.nombre below header
  - Draw "Escuela:" label and entrada.escuela below name
  - Generate QR code from entrada.uuid using segno into BytesIO PNG
  - Embed QR image at bottom of PDF using ImageReader + drawImage
  - Handle long text by truncating or reducing font size to fit 5cm width
  - Call showPage() and save(), seek(0) on buffer, return BytesIO

- [x] T003 [P] [US1] Create PDF download controller endpoint in app/controllers/entrada_pdf_controller.py
  - Import APIRouter, Depends, get_session, get_current_user
  - Import StreamingResponse from fastapi.responses
  - Import EntradaPdfService and Entrada model
  - Create router = APIRouter()
  - Implement GET /{id}/pdf endpoint:
    - Receive id as path parameter (int)
    - Query Entrada by id from database session
    - If not found: raise HTTPException 404 "Entrada no encontrada"
    - Call EntradaPdfService().generate_pdf(entrada)
    - Return StreamingResponse with media_type="application/pdf"
    - Set Content-Disposition header: attachment; filename="entrada-{id}.pdf"

- [x] T004 [US1] Register entrada PDF router in app/api/routes/router.py
  - Import entrada_pdf_controller
  - Add api_router.include_router() for entrada_pdf with:
    - prefix="/api/entradas"
    - tags=["entradas"]
    - dependencies=[Depends(get_current_user)]

**Checkpoint**: At this point, User Story 1 should be fully functional - a user can request GET /api/entradas/{id}/pdf and receive a downloadable PDF with the correct content and dimensions.

---

## Phase 4: User Story 2 - Manejo de errores en la generación (Priority: P2)

**Goal**: Return clear, appropriate error responses when PDF generation is requested for non-existent entries or with invalid IDs.

**Independent Test**: Request PDF generation with a non-existent ID (e.g., 9999) and verify a 404 error with a clear message is returned. Request with an invalid ID format and verify a 422 validation error is returned.

### Implementation for User Story 2

- [x] T005 [US2] Add error handling for edge cases in app/controllers/entrada_pdf_controller.py
  - Verify 404 response for non-existent entrada IDs includes descriptive message "Entrada no encontrada"
  - Verify FastAPI's built-in path parameter validation handles non-integer ID formats (returns 422)
  - Ensure no unhandled exceptions leak to the client during PDF generation failures

**Checkpoint**: Both user stories should now work correctly - successful PDF generation (US1) and proper error handling (US2).

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T006 Run manual verification: create an entrada, download its PDF, verify content and dimensions per quickstart.md
- [x] T007 Verify QR code is scannable and returns the correct UUID

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: No tasks - existing infrastructure is sufficient
- **User Story 1 (Phase 3)**: Depends on Phase 1 (dependencies installed)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (controller must exist to add error handling)
- **Polish (Phase 5)**: Depends on Phase 3 and Phase 4

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup (Phase 1). Requires Entrada model from feature 002-entradas-crud to exist.
- **User Story 2 (P2)**: Depends on US1 controller (T003) being complete. Error handling is added to the same controller file.

### Within Each User Story

- T002 (service) and T003 (controller) can be created in parallel [P] since they are different files
- T004 (router registration) depends on T003 (controller must exist to import)
- T005 (error handling) depends on T003 (controller must exist to enhance)

### Parallel Opportunities

- T002 and T003 can be created in parallel (different files, no direct dependency)
- T006 and T007 can be run in parallel (independent verification tasks)

---

## Parallel Example: User Story 1

```bash
# Launch service and controller creation in parallel:
Task: "Create PDF generation service in app/services/entrada_pdf_service.py"
Task: "Create PDF download controller in app/controllers/entrada_pdf_controller.py"

# Then sequentially:
Task: "Register router in app/api/routes/router.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Install dependencies (T001)
2. Complete Phase 3: Implement service (T002) + controller (T003) in parallel, then register router (T004)
3. **STOP and VALIDATE**: Test by downloading a PDF for an existing entrada
4. Deploy/demo if ready

### Incremental Delivery

1. Install dependencies → Setup ready
2. Add User Story 1 (PDF generation) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (error handling) → Test independently → Deploy/Demo
4. Polish → Verify QR scanning and manual validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This feature has only 2 new files to create + 1 file to modify + 1 dependency update
- Feature depends on Entrada model from 002-entradas-crud being implemented first
- No test tasks included (not requested in spec)
- Commit after each task or logical group
