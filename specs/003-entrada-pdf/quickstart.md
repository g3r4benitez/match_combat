# Quickstart: Generación de PDF de Entrada con QR

**Feature**: 003-entrada-pdf
**Prerequisite**: Feature 002-entradas-crud (entidad Entrada debe existir)

## Dependencias nuevas

```bash
pip install reportlab segno
```

Agregar al `requirements.txt`:
```
reportlab>=4.0
segno>=1.6
```

## Archivos a crear/modificar

### Nuevos archivos

| Archivo | Propósito |
|---------|-----------|
| `app/services/entrada_pdf_service.py` | Lógica de generación del PDF con QR |
| `app/controllers/entrada_pdf_controller.py` | Endpoint GET /api/entradas/{id}/pdf |

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `app/api/routes/router.py` | Registrar el nuevo router de entrada_pdf |
| `requirements.txt` | Agregar reportlab y segno |

## Flujo de implementación

1. Instalar dependencias (`reportlab`, `segno`)
2. Crear el servicio `entrada_pdf_service.py`:
   - Método que recibe una Entrada y genera el PDF en BytesIO
   - Usar reportlab con `Canvas(buffer, pagesize=(5*cm, 12*cm))`
   - Generar QR con segno usando el UUID de la entrada
   - Embeber QR en el PDF con `drawImage`
3. Crear el controlador `entrada_pdf_controller.py`:
   - Endpoint `GET /api/entradas/{id}/pdf`
   - Buscar la Entrada por ID usando el servicio existente
   - Llamar al servicio de PDF para generar el documento
   - Retornar `StreamingResponse` con content-disposition attachment
4. Registrar el router en `router.py`
5. Verificar manualmente creando una entrada y descargando su PDF

## Verificación rápida

```bash
# 1. Crear una entrada de prueba (requiere autenticación)
curl -X POST http://localhost:8000/api/entradas/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan Pérez", "escuela": "Escuela Norte"}'

# 2. Descargar el PDF (usar el ID retornado)
curl -X GET http://localhost:8000/api/entradas/1/pdf \
  -H "Authorization: Bearer <token>" \
  -o entrada-1.pdf

# 3. Abrir el PDF y verificar contenido
xdg-open entrada-1.pdf  # Linux
```
