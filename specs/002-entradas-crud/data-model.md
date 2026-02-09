# Data Model: Entradas CRUD

**Feature**: 002-entradas-crud
**Date**: 2026-02-09

## Entities

### Entrada

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Identificador numérico |
| nombre | String | required, non-empty | Nombre del asistente |
| escuela | String | required, non-empty | Institución educativa |
| usada | Integer | default=0, values: 0 or 1 | 0=pendiente, 1=usada |
| uuid | String | unique, auto-generated | Código de validación |

### DTOs

**EntradaCreateDTO** (para crear):
- nombre: str (required, min_length=1)
- escuela: str (required, min_length=1)

**EntradaUpdateDTO** (para actualizar):
- nombre: Optional[str] (min_length=1 if provided)
- escuela: Optional[str] (min_length=1 if provided)
- usada: Optional[int] (0 or 1 if provided)

## Relaciones

- Sin relaciones con otras entidades.
- Entidad independiente.
