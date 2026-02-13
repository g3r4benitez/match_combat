# Feature Specification: Imagen de Patrocinadores en Footer del PDF de Entrada

**Feature Branch**: `005-pdf-footer-sponsors`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "agregar una imagen al footer del pdf generado en la clase EntradaPdfService, la imagen a agrear al footer se encuentra en static/images/sponsors.png"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mostrar patrocinadores en la entrada PDF (Priority: P1)

Como organizador del evento, quiero que cada entrada PDF generada muestre la imagen de los patrocinadores en el pie de página, para cumplir con los compromisos de visibilidad con los sponsors del evento.

**Why this priority**: Es la funcionalidad principal y única de esta feature. Los patrocinadores necesitan visibilidad en cada entrada impresa que se distribuya en el evento.

**Independent Test**: Se puede verificar generando cualquier entrada PDF y confirmando que la imagen de patrocinadores aparece en la parte inferior de la página, debajo del código QR.

**Acceptance Scenarios**:

1. **Given** una entrada existente en el sistema, **When** se genera el PDF de la entrada, **Then** la imagen de patrocinadores (`sponsors.png`) aparece en el pie de página debajo del código QR.
2. **Given** una entrada existente en el sistema, **When** se genera el PDF de la entrada, **Then** la imagen de patrocinadores se muestra completa, sin recortes, y centrada horizontalmente dentro del ancho de contenido disponible.
3. **Given** una entrada existente en el sistema, **When** se genera el PDF de la entrada, **Then** el código QR y los datos del competidor (nombre, escuela) siguen siendo legibles y no se superponen con la imagen de patrocinadores.

---

### Edge Cases

- ¿Qué pasa si el archivo `sponsors.png` no existe en la ruta esperada? El sistema debe generar el PDF sin la imagen de patrocinadores en lugar de fallar con un error.
- ¿Qué pasa si la imagen tiene un tamaño diferente al esperado? La imagen debe escalarse proporcionalmente para ajustarse al ancho de contenido disponible, manteniendo su relación de aspecto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar la imagen ubicada en `static/images/sponsors.png` en el pie de página de cada entrada PDF generada.
- **FR-002**: La imagen DEBE estar centrada horizontalmente dentro del área de contenido de la página.
- **FR-003**: La imagen DEBE escalarse proporcionalmente para ajustarse al ancho de contenido disponible, sin deformarse ni recortarse.
- **FR-004**: La imagen DEBE posicionarse debajo del código QR, en la zona inferior de la página.
- **FR-005**: Los elementos existentes del PDF (encabezado del evento, nombre, escuela, código QR) DEBEN permanecer visibles y legibles sin superposición con la imagen de patrocinadores.
- **FR-006**: Si el archivo de imagen no se encuentra en la ruta esperada, el sistema DEBE generar el PDF normalmente sin la imagen de patrocinadores (degradación graceful).

## Assumptions

- La imagen `sponsors.png` ya existe en `static/images/sponsors.png` y tiene formato PNG válido (confirmado: 727 × 253 px, RGBA).
- La imagen es una franja horizontal de logos de patrocinadores, lo cual se adapta bien al formato angosto de la entrada (5 cm de ancho).
- El tamaño de página actual (5 cm × 10 cm) tiene espacio suficiente para acomodar la imagen en el footer. Es posible que se necesite un ajuste menor en la posición vertical del QR para hacer espacio.
- La imagen de patrocinadores es la misma para todas las entradas (no varía por competidor ni por evento).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las entradas PDF generadas incluyen la imagen de patrocinadores en el pie de página cuando el archivo de imagen existe.
- **SC-002**: La imagen de patrocinadores es completamente visible y legible en la entrada impresa.
- **SC-003**: Todos los elementos previamente existentes en la entrada (nombre del evento, nombre del competidor, escuela, código QR) permanecen legibles sin superposición.
- **SC-004**: La generación del PDF no falla cuando el archivo de imagen de patrocinadores no está disponible.
