# Feature Specification: Entradas CRUD

**Feature Branch**: `002-entradas-crud`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Agrega una entidad/model llamada entradas, que tenga los campos id, nombre campo obligatorio de tipo string, escuela campo obligatorio de tipo string, usada (0 pendiente, 1 usada), uuid es un identificador unico luego se usara para validar el ingreso y determinar si la entrada fue usada o no, debes crear el crud, los controladores, endpoints, servicios, etc."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear una nueva entrada (Priority: P1)

Un administrador necesita registrar una nueva entrada en el sistema proporcionando el nombre del asistente y su escuela. Al crear la entrada, el sistema genera automáticamente un identificador único (UUID) que servirá como código de la entrada. La entrada se crea con estado "pendiente" (no usada).

**Why this priority**: La creación de entradas es la funcionalidad base sin la cual ninguna otra operación tiene sentido. Es el punto de partida del flujo completo.

**Independent Test**: Se puede probar creando una entrada con nombre y escuela válidos, verificando que se devuelve la entrada con su UUID generado y estado pendiente.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** envía una solicitud para crear una entrada con nombre "Juan Pérez" y escuela "Escuela Primaria Norte", **Then** el sistema crea la entrada con estado pendiente (usada=0) y genera un UUID único.
2. **Given** un usuario autenticado, **When** envía una solicitud para crear una entrada sin el campo nombre, **Then** el sistema rechaza la solicitud indicando que el nombre es obligatorio.
3. **Given** un usuario autenticado, **When** envía una solicitud para crear una entrada sin el campo escuela, **Then** el sistema rechaza la solicitud indicando que la escuela es obligatoria.

---

### User Story 2 - Consultar entradas (Priority: P1)

Un administrador necesita listar todas las entradas registradas y también consultar una entrada específica por su ID o UUID para verificar su información y estado.

**Why this priority**: La consulta es esencial para la operación del sistema ya que permite verificar las entradas existentes y su estado actual.

**Independent Test**: Se puede probar listando las entradas existentes y consultando una entrada específica por ID, verificando que se retorna la información completa.

**Acceptance Scenarios**:

1. **Given** entradas existentes en el sistema, **When** se solicita el listado de todas las entradas, **Then** el sistema retorna todas las entradas con sus campos completos (id, nombre, escuela, usada, uuid).
2. **Given** una entrada existente con ID 5, **When** se consulta la entrada por ID 5, **Then** el sistema retorna la información completa de esa entrada.
3. **Given** ninguna entrada existente, **When** se solicita el listado de entradas, **Then** el sistema retorna una lista vacía.
4. **Given** un ID que no existe, **When** se consulta por ese ID, **Then** el sistema informa que la entrada no fue encontrada.

---

### User Story 3 - Validar entrada por UUID (Priority: P1)

Un operador necesita validar una entrada usando su UUID para determinar si ya fue utilizada o si está pendiente. Este es el flujo principal de uso de las entradas: al presentar el UUID, el sistema indica si la entrada es válida y si puede ser usada.

**Why this priority**: Esta es la funcionalidad core del sistema de entradas: poder validar si una entrada es válida y si ya fue usada o no mediante su UUID único.

**Independent Test**: Se puede probar consultando una entrada por su UUID y verificando que el sistema retorna el estado correcto (pendiente o usada).

**Acceptance Scenarios**:

1. **Given** una entrada con estado pendiente (usada=0), **When** se consulta por su UUID, **Then** el sistema indica que la entrada es válida y no ha sido usada.
2. **Given** una entrada con estado usada (usada=1), **When** se consulta por su UUID, **Then** el sistema indica que la entrada ya fue utilizada.
3. **Given** un UUID que no existe en el sistema, **When** se consulta por ese UUID, **Then** el sistema indica que la entrada no fue encontrada.

---

### User Story 4 - Actualizar una entrada (Priority: P2)

Un administrador necesita poder actualizar la información de una entrada existente, como corregir el nombre o la escuela, o cambiar manualmente el estado de usada.

**Why this priority**: La actualización permite corregir errores de captura y gestionar manualmente el estado de las entradas cuando sea necesario.

**Independent Test**: Se puede probar actualizando el nombre de una entrada existente y verificando que el cambio se persiste correctamente.

**Acceptance Scenarios**:

1. **Given** una entrada existente, **When** se actualiza el nombre a "María López", **Then** el sistema persiste el cambio y retorna la entrada actualizada.
2. **Given** una entrada existente con estado pendiente, **When** se actualiza el campo usada a 1, **Then** la entrada queda marcada como usada.
3. **Given** un ID de entrada que no existe, **When** se intenta actualizar, **Then** el sistema informa que la entrada no fue encontrada.

---

### User Story 5 - Eliminar una entrada (Priority: P3)

Un administrador necesita poder eliminar una entrada del sistema cuando fue creada por error o ya no es necesaria.

**Why this priority**: La eliminación es una operación menos frecuente pero necesaria para la gestión completa del ciclo de vida de las entradas.

**Independent Test**: Se puede probar eliminando una entrada existente y verificando que ya no aparece en el listado.

**Acceptance Scenarios**:

1. **Given** una entrada existente con ID 5, **When** se solicita eliminar la entrada con ID 5, **Then** el sistema elimina la entrada y confirma la operación.
2. **Given** un ID de entrada que no existe, **When** se intenta eliminar, **Then** el sistema informa que la entrada no fue encontrada.

---

### Edge Cases

- Que sucede cuando se intenta crear una entrada con nombre o escuela vacíos (strings vacíos): el sistema debe rechazar la solicitud.
- Que sucede cuando se intenta crear una entrada con campos que exceden la longitud máxima razonable: el sistema debe validar y rechazar.
- Que sucede cuando se busca por un UUID con formato inválido: el sistema debe retornar un error adecuado.
- Que sucede cuando se intenta actualizar el UUID de una entrada: el UUID no debe ser modificable una vez creado.
- Que sucede si hay entradas duplicadas con el mismo nombre y escuela: el sistema debe permitirlo ya que el UUID es el identificador único, diferentes personas pueden tener el mismo nombre y escuela.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir crear una nueva entrada proporcionando nombre (obligatorio, string) y escuela (obligatorio, string).
- **FR-002**: El sistema DEBE generar automáticamente un UUID único para cada entrada al momento de la creación.
- **FR-003**: El sistema DEBE asignar el estado "pendiente" (usada=0) a toda entrada recién creada.
- **FR-004**: El sistema DEBE permitir listar todas las entradas con sus campos completos.
- **FR-005**: El sistema DEBE permitir consultar una entrada individual por su ID.
- **FR-006**: El sistema DEBE permitir consultar una entrada por su UUID para validar su estado.
- **FR-007**: El sistema DEBE permitir actualizar los campos nombre, escuela y usada de una entrada existente.
- **FR-008**: El sistema DEBE impedir la modificación del UUID de una entrada una vez creada.
- **FR-009**: El sistema DEBE permitir eliminar una entrada por su ID.
- **FR-010**: El sistema DEBE validar que nombre y escuela no estén vacíos al crear o actualizar una entrada.
- **FR-011**: El sistema DEBE retornar un error apropiado cuando se intente acceder, actualizar o eliminar una entrada que no existe.
- **FR-012**: El campo usada solo DEBE aceptar los valores 0 (pendiente) y 1 (usada).

### Key Entities

- **Entrada**: Representa un ticket o boleto de ingreso a un evento. Atributos principales: identificador numérico auto-incremental (id), nombre del asistente (nombre), institución educativa del asistente (escuela), estado de uso de la entrada (usada: 0=pendiente, 1=usada), y un identificador único universal (uuid) que sirve como código de validación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden crear una nueva entrada proporcionando nombre y escuela en menos de 5 segundos.
- **SC-002**: Los usuarios pueden consultar el estado de una entrada por UUID y obtener respuesta inmediata sobre si está pendiente o usada.
- **SC-003**: El 100% de las entradas creadas reciben un UUID único que no se repite en el sistema.
- **SC-004**: Las operaciones de listado, consulta, creación, actualización y eliminación funcionan correctamente y retornan las respuestas esperadas.
- **SC-005**: El sistema rechaza el 100% de las solicitudes de creación que no incluyan nombre o escuela.

## Assumptions

- El sistema ya cuenta con autenticación JWT implementada (feature 001-jwt-auth) y los endpoints de entradas estarán protegidos por autenticación.
- El UUID se genera del lado del servidor al crear la entrada; el cliente no proporciona este valor.
- No se requiere paginación para el listado de entradas en esta primera versión.
- No se requiere soft-delete; la eliminación es permanente.
- El campo "usada" es un valor numérico entero (0 o 1), no un booleano.
