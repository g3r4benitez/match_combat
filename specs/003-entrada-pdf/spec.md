# Feature Specification: Generación de PDF de Entrada con QR

**Feature Branch**: `003-entrada-pdf`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Crea un endpoint para generar un pdf con informacion de una entrada, debe tener un encabezado que temporalmente diga 'Titulo Evento', nombre: que es el nombre de la persona titular de la entrada, escuela, y un codigo qr que contenga el uuid, debe ser en formato vertical de 5 por 12 centimetros aproximadamente. El endpoint recibe como parametro el id de la entrada. y el pdf debe ser descargable"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generar y descargar PDF de una entrada (Priority: P1)

Un administrador necesita generar un documento PDF descargable para una entrada específica. El PDF funciona como un boleto/ticket imprimible que contiene la información del asistente y un código QR para validación rápida. El administrador solicita la generación proporcionando el ID de la entrada y recibe el archivo PDF listo para descargar e imprimir.

**Why this priority**: Esta es la única y principal funcionalidad de este feature. Sin ella, no hay forma de entregar un boleto físico o digital al asistente.

**Independent Test**: Se puede probar solicitando la generación del PDF de una entrada existente, descargando el archivo y verificando que contiene la información correcta y el código QR es escaneable.

**Acceptance Scenarios**:

1. **Given** una entrada existente con id=1, nombre="Juan Pérez", escuela="Escuela Norte", uuid="abc-123", **When** se solicita generar el PDF de la entrada con id=1, **Then** el sistema retorna un archivo PDF descargable con el contenido correcto.
2. **Given** el PDF generado, **When** se examina su contenido, **Then** muestra el encabezado "Titulo Evento", el nombre del titular, la escuela, y un código QR que al escanearse devuelve el UUID de la entrada.
3. **Given** el PDF generado, **When** se verifican sus dimensiones, **Then** el documento tiene un formato vertical (portrait) de aproximadamente 5 cm de ancho por 12 cm de alto.
4. **Given** el PDF generado, **When** el usuario lo recibe en su navegador, **Then** se presenta como una descarga de archivo (no se muestra inline en el navegador).

---

### User Story 2 - Manejo de errores en la generación (Priority: P2)

Cuando se solicita generar un PDF para una entrada que no existe, el sistema debe informar adecuadamente al usuario en lugar de generar un error inesperado.

**Why this priority**: El manejo correcto de errores es esencial para una buena experiencia de usuario, pero la generación exitosa del PDF es más prioritaria.

**Independent Test**: Se puede probar solicitando la generación de un PDF con un ID de entrada inexistente y verificando que se retorna un mensaje de error claro.

**Acceptance Scenarios**:

1. **Given** que no existe una entrada con id=9999, **When** se solicita generar el PDF para la entrada con id=9999, **Then** el sistema retorna un error indicando que la entrada no fue encontrada.
2. **Given** un ID de entrada con formato inválido (no numérico), **When** se solicita generar el PDF, **Then** el sistema retorna un error de validación apropiado.

---

### Edge Cases

- Que sucede cuando el nombre del titular es muy largo y excede el espacio disponible en el PDF: el texto debe ajustarse (truncarse o reducir el tamaño de fuente) para caber en el ancho del documento.
- Que sucede cuando el nombre de la escuela es muy largo: mismo tratamiento que el nombre, debe ajustarse al espacio disponible.
- Que sucede cuando se generan múltiples PDFs simultáneamente para diferentes entradas: cada solicitud debe generar su PDF de forma independiente sin interferir con las demás.
- Que sucede si el UUID contiene caracteres especiales: el código QR debe codificar el UUID tal como está almacenado, sin alteraciones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE generar un documento PDF cuando se solicite proporcionando el ID de una entrada existente.
- **FR-002**: El PDF DEBE contener un encabezado con el texto "Titulo Evento" (texto temporal/placeholder).
- **FR-003**: El PDF DEBE mostrar el nombre del titular de la entrada.
- **FR-004**: El PDF DEBE mostrar la escuela del titular de la entrada.
- **FR-005**: El PDF DEBE incluir un código QR que contenga el UUID de la entrada.
- **FR-006**: El código QR DEBE ser escaneable y devolver el UUID correcto de la entrada.
- **FR-007**: El PDF DEBE tener formato vertical (portrait) con dimensiones aproximadas de 5 cm de ancho por 12 cm de alto.
- **FR-008**: El PDF DEBE ser retornado como un archivo descargable (content-disposition: attachment).
- **FR-009**: El sistema DEBE retornar un error claro cuando se solicita generar un PDF para una entrada que no existe.
- **FR-010**: El contenido del PDF (nombre, escuela) DEBE ajustarse al espacio disponible cuando los textos sean largos.

### Key Entities

- **Entrada** (existente, de feature 002-entradas-crud): La entidad de la cual se obtienen los datos para generar el PDF. Campos utilizados: id (para buscar la entrada), nombre (mostrado en el PDF), escuela (mostrada en el PDF), uuid (codificado en el QR).
- **PDF de Entrada**: Documento generado bajo demanda, no se persiste. Contiene encabezado del evento, datos del titular y código QR. Formato vertical de 5x12 cm aproximadamente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden generar y descargar el PDF de una entrada en menos de 5 segundos desde que realizan la solicitud.
- **SC-002**: El 100% de los códigos QR generados son escaneables y contienen el UUID correcto de la entrada.
- **SC-003**: El 100% de los PDFs generados contienen la información correcta del titular (nombre y escuela) correspondiente a la entrada solicitada.
- **SC-004**: El PDF se descarga correctamente en los navegadores principales sin necesidad de pasos adicionales por parte del usuario.
- **SC-005**: Las dimensiones del PDF se mantienen consistentemente en aproximadamente 5x12 cm para todas las entradas generadas.

## Assumptions

- La entidad Entrada ya existe en el sistema (feature 002-entradas-crud) y contiene los campos necesarios: id, nombre, escuela, uuid.
- El endpoint estará protegido por autenticación JWT (feature 001-jwt-auth).
- El texto del encabezado "Titulo Evento" es temporal y será reemplazado en una futura iteración, posiblemente con un campo configurable.
- El PDF se genera bajo demanda y no se almacena en el servidor; se genera y retorna directamente al cliente.
- No se requiere un diseño gráfico elaborado para el PDF; un diseño limpio y funcional es suficiente.
- La disposición de los elementos en el PDF sigue un orden vertical de arriba a abajo: encabezado, nombre, escuela, código QR.
- No se requiere soporte para generación masiva (batch) de PDFs en esta versión; se genera uno por solicitud.
