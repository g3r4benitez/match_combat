# Data Model: Generación de PDF de Entrada con QR

**Feature**: 003-entrada-pdf
**Date**: 2026-02-09

## Entities

### Entrada (existente - de feature 002-entradas-crud)

Este feature no crea nuevas entidades. Utiliza la entidad **Entrada** existente como fuente de datos para la generación del PDF.

**Campos utilizados**:

| Campo | Tipo | Uso en PDF |
|-------|------|------------|
| id | Integer (PK) | Parámetro de entrada del endpoint |
| nombre | String (required) | Mostrado como nombre del titular |
| escuela | String (required) | Mostrado como escuela del titular |
| uuid | String (unique) | Codificado en el código QR |

### PDF de Entrada (artefacto generado, no persistido)

El PDF es un documento generado bajo demanda, no se almacena en base de datos ni en el sistema de archivos.

**Estructura del documento**:

```
┌─────────────────────┐  ← 5 cm ancho
│                     │
│   TITULO EVENTO     │  ← Encabezado (placeholder temporal)
│                     │
│   Nombre:           │
│   [nombre titular]  │  ← Campo nombre de Entrada
│                     │
│   Escuela:          │
│   [escuela]         │  ← Campo escuela de Entrada
│                     │
│   ┌───────────┐     │
│   │           │     │
│   │  QR Code  │     │  ← UUID codificado como QR
│   │           │     │
│   └───────────┘     │
│                     │
└─────────────────────┘  ← 12 cm alto
```

**Dimensiones**: 5 cm (ancho) x 12 cm (alto), formato portrait.

## Relaciones

- El PDF depende de una **Entrada** existente (relación de lectura).
- No hay relaciones bidireccionales ni foreign keys nuevas.

## Validación

- El ID de entrada proporcionado debe corresponder a una Entrada existente.
- No se aplican validaciones adicionales a los datos de la Entrada para la generación del PDF.
