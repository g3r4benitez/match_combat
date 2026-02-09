# Tasks: Entradas CRUD

**Input**: Design documents from `/specs/002-entradas-crud/`
**Tests**: No tests explicitly requested.
**Organization**: Tasks grouped by user story.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

**Purpose**: Model and DTOs creation

- [x] T001 Create Entrada model in app/models/entrada.py
- [x] T002 [P] Create EntradaCreateDTO and EntradaUpdateDTO in app/entities/entrada_entities.py
- [x] T003 Register Entrada model import in app/core/database.py

---

## Phase 2: Foundational

**Purpose**: Service layer with business logic

- [x] T004 Create EntradaService with CRUD methods in app/services/entrada_service.py

**Checkpoint**: Service layer ready

---

## Phase 3: User Story 1 - Crear entrada (P1) + User Story 2 - Consultar entradas (P1) + User Story 3 - Validar por UUID (P1)

**Goal**: Create, list, get by ID, get by UUID endpoints

- [x] T005 [US1][US2][US3] Create entrada_controller.py with POST, GET list, GET by ID, GET by UUID endpoints in app/controllers/entrada_controller.py

**Checkpoint**: Create and read operations functional

---

## Phase 4: User Story 4 - Actualizar entrada (P2) + User Story 5 - Eliminar entrada (P3)

**Goal**: Update and delete endpoints

- [x] T006 [US4][US5] Add PUT and DELETE endpoints to app/controllers/entrada_controller.py

---

## Phase 5: Integration

- [x] T007 Register entrada router in app/api/routes/router.py

---

## Phase 6: Polish

- [x] T008 Verify all CRUD operations work via import test

---

## Dependencies

- T001 → T003 → T004 → T005 → T006 → T007 → T008
- T002 runs in parallel with T001
