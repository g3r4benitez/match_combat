# Tasks: PDF Footer Sponsors Image

**Input**: Design documents from `/specs/005-pdf-footer-sponsors/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not requested — manual verification only (no test suite exists in this project).

**Organization**: Single user story feature. No setup or foundational phases needed — no new dependencies, no new infrastructure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: User Story 1 - Mostrar patrocinadores en la entrada PDF (Priority: P1) 🎯 MVP

**Goal**: Display the sponsors banner image (`static/images/sponsors.png`) at the bottom of every entrada PDF, below the QR code, with graceful degradation if the image file is missing.

**Independent Test**: Generate any entrada PDF via `GET /api/entradas/{id}/pdf` and confirm the sponsors image appears at the bottom of the page, below the QR code, without overlapping any existing elements.

### Implementation for User Story 1

- [x] T001 [US1] Add imports (`pathlib.Path`, `logging`) and `SPONSORS_IMAGE_PATH` constant using `ROOT_DIR` from config in `app/services/entrada_pdf_service.py`
  - Import `from pathlib import Path` and `import logging`
  - Import `ROOT_DIR` from `app.core.config`
  - Add module-level constant: `SPONSORS_IMAGE_PATH = Path(ROOT_DIR) / "static" / "images" / "sponsors.png"`
  - Add module-level logger: `logger = logging.getLogger(__name__)`

- [x] T002 [US1] Add `_draw_sponsors_footer` private method to `EntradaPdfService` in `app/services/entrada_pdf_service.py`
  - Signature: `def _draw_sponsors_footer(self, c: canvas.Canvas) -> float`
  - Load image from `SPONSORS_IMAGE_PATH` using `ImageReader`
  - Calculate proportional height: `img_width = CONTENT_WIDTH`, `img_height = CONTENT_WIDTH * (original_height / original_width)`
  - Center horizontally: `x = (PAGE_WIDTH - img_width) / 2`
  - Position at bottom: `y = MARGIN`
  - Draw image with `c.drawImage()`
  - Return `img_height` on success
  - Wrap entire method body in `try/except Exception`: log warning and return `0.0` on failure
  - Per research Decision 3: catch broadly to handle missing files, corrupted images, and permission issues

- [x] T003 [US1] Modify QR code positioning in `generate_pdf()` method to account for sponsors footer height in `app/services/entrada_pdf_service.py`
  - Call `sponsors_height = self._draw_sponsors_footer(c)` before the QR code section
  - Change QR y-position from `qr_y = MARGIN + 0.3 * cm` to `qr_y = MARGIN + sponsors_height + 0.2 * cm` (adds dynamic offset based on footer image height, plus 0.2cm gap)
  - Per research Decision 1: QR stays in shifted-up position regardless of whether image loaded successfully

---

## Phase 2: Polish & Verification

**Purpose**: Validate the complete implementation

- [x] T004 Run manual verification per `specs/005-pdf-footer-sponsors/quickstart.md`
  - Generate a PDF and confirm sponsors image is visible at footer
  - Confirm QR code, name, school, and header remain legible with no overlap
  - Test graceful degradation by temporarily renaming `sponsors.png`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (US1)**: No dependencies — can start immediately (existing project, existing file)
- **Phase 2 (Polish)**: Depends on Phase 1 completion

### Within User Story 1

```
T001 (imports/constants)
  └─→ T002 (_draw_sponsors_footer method)
       └─→ T003 (modify QR positioning in generate_pdf)
            └─→ T004 (manual verification)
```

All tasks are sequential — they modify the same file (`app/services/entrada_pdf_service.py`) and each depends on the previous.

### Parallel Opportunities

None — single file modification with sequential dependencies. This is a 4-task feature that should be implemented in order.

---

## Implementation Strategy

### MVP (Complete Feature)

1. Complete T001–T003: All changes in `app/services/entrada_pdf_service.py`
2. Complete T004: Manual verification
3. **DONE**: Feature is complete — single user story, single file

### Estimated Scope

- **Total tasks**: 4
- **Files modified**: 1 (`app/services/entrada_pdf_service.py`)
- **New files**: 0
- **New dependencies**: 0

---

## Notes

- All implementation tasks target a single file — commit as one logical change
- The QR position offset uses `sponsors_height` dynamically, so if the image is absent (returns 0), the layout gracefully falls back to a slightly shifted but acceptable position
- No tests phase included — project has no test infrastructure per plan.md
