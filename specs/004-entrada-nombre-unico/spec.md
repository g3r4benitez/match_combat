# Feature Specification: Nombre Único en Entradas

**Feature Branch**: `004-entrada-nombre-unico`
**Created**: 2026-02-11
**Status**: Draft
**Input**: User description: "el campo nombre de las entradas debera ser unico, y no puede repetirse."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prevenir creación de entradas con nombre duplicado (Priority: P1)

Un administrador intenta crear una nueva entrada con un nombre que ya existe en el sistema. El sistema rechaza la operación y muestra un mensaje claro indicando que ya existe una entrada con ese nombre.

**Why this priority**: La prevención de duplicados al crear es el caso más frecuente y crítico. Sin esta restricción, se generan entradas duplicadas que causan confusión y problemas operativos.

**Independent Test**: Se puede probar creando una entrada con un nombre existente y verificando que el sistema la rechaza con un mensaje de error descriptivo.

**Acceptance Scenarios**:

1. **Given** una entrada con nombre "VIP Mesa 1" ya existe, **When** el administrador intenta crear otra entrada con nombre "VIP Mesa 1", **Then** el sistema rechaza la creación y muestra un mensaje indicando que el nombre ya está en uso.
2. **Given** una entrada con nombre "VIP Mesa 1" ya existe, **When** el administrador crea una entrada con nombre "VIP Mesa 2", **Then** el sistema crea la entrada exitosamente.
3. **Given** una entrada con nombre "VIP Mesa 1" ya existe, **When** el administrador intenta crear otra con nombre "  VIP Mesa 1  " (con espacios), **Then** el sistema rechaza la creación, ya que el nombre se normaliza eliminando espacios al inicio y al final.

---

### User Story 2 - Prevenir actualización que genere nombre duplicado (Priority: P2)

Un administrador intenta actualizar el nombre de una entrada existente a un nombre que ya está en uso por otra entrada. El sistema rechaza la operación e informa del conflicto.

**Why this priority**: Complementa la restricción de creación para cubrir todos los puntos de entrada donde se asigna un nombre. Sin esto, un usuario podría generar duplicados a través de la edición.

**Independent Test**: Se puede probar actualizando una entrada para que tenga el nombre de otra entrada existente y verificando el rechazo.

**Acceptance Scenarios**:

1. **Given** existen entradas "VIP Mesa 1" y "VIP Mesa 2", **When** el administrador actualiza "VIP Mesa 2" cambiando su nombre a "VIP Mesa 1", **Then** el sistema rechaza la actualización e indica que el nombre ya está en uso.
2. **Given** existe la entrada "VIP Mesa 1", **When** el administrador actualiza esa misma entrada sin cambiar el nombre (cambia otro campo), **Then** el sistema permite la actualización exitosamente.
3. **Given** existe la entrada "VIP Mesa 1", **When** el administrador actualiza esa misma entrada guardando el mismo nombre "VIP Mesa 1", **Then** el sistema permite la actualización (no se detecta conflicto consigo misma).

---

### Edge Cases

- ¿Qué pasa si dos administradores intentan crear una entrada con el mismo nombre al mismo tiempo? El sistema debe garantizar que solo una se cree exitosamente; la segunda debe recibir un error de nombre duplicado.
- ¿Qué pasa si se intenta crear una entrada con nombre que difiere solo en mayúsculas/minúsculas (ej. "VIP Mesa 1" vs "vip mesa 1")? **Asunción**: La comparación de unicidad es exacta (case-sensitive), ya que los nombres de entradas suelen ser etiquetas formales que respetan capitalización.
- ¿Qué pasa si se elimina una entrada? Su nombre queda disponible para ser reutilizado por una nueva entrada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE rechazar la creación de una entrada cuando ya existe otra entrada con el mismo nombre.
- **FR-002**: El sistema DEBE rechazar la actualización de una entrada cuando el nuevo nombre ya está en uso por otra entrada diferente.
- **FR-003**: El sistema DEBE permitir actualizar una entrada conservando su propio nombre sin generar error de duplicado.
- **FR-004**: El sistema DEBE normalizar el nombre eliminando espacios al inicio y al final antes de evaluar la unicidad (consistente con la validación existente).
- **FR-005**: El sistema DEBE retornar un mensaje de error claro cuando se rechace una operación por nombre duplicado, indicando que el nombre ya está en uso.
- **FR-006**: El sistema DEBE garantizar la unicidad del nombre a nivel de persistencia para prevenir condiciones de carrera.

### Key Entities

- **Entrada**: Representa una entrada (ticket) para un evento. Atributos clave: nombre (identificador textual único), escuela, estado de uso (usada), identificador UUID. La restricción de unicidad aplica al campo nombre.

## Assumptions

- La comparación de unicidad del nombre es exacta (case-sensitive). "VIP Mesa 1" y "vip mesa 1" se consideran nombres diferentes.
- La normalización de espacios ya existente (strip/trim en la validación del DTO) se aplica antes de la verificación de unicidad.
- Al eliminar una entrada, su nombre queda disponible para reutilización.
- No se requieren cambios en los permisos o autenticación existentes; la restricción aplica para cualquier usuario autenticado que tenga acceso a gestionar entradas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de crear una entrada con un nombre ya existente son rechazados con un mensaje de error descriptivo.
- **SC-002**: El 100% de los intentos de actualizar una entrada a un nombre ya en uso por otra entrada son rechazados con un mensaje de error descriptivo.
- **SC-003**: Las operaciones de creación y actualización de entradas con nombres únicos siguen funcionando sin cambios en la experiencia del usuario.
- **SC-004**: No existen entradas con nombres duplicados en el sistema después de implementar la restricción.
