# Quickstart: PDF Footer Sponsors Image

## Prerequisites

- Python 3.11+ with project dependencies installed (`reportlab`, `segno`)
- The file `static/images/sponsors.png` present in the project root
- At least one `Entrada` record in the database

## Verify the Change

1. Start the application:
   ```bash
   cd src && uvicorn app.main:app --reload
   ```

2. Generate a PDF for an existing entrada:
   ```bash
   curl -o entrada-test.pdf http://localhost:8000/api/entradas/1/pdf
   ```

3. Open `entrada-test.pdf` and verify:
   - The sponsors banner appears at the bottom of the page
   - The sponsors image is fully visible, not cropped
   - The QR code is above the sponsors image with a small gap
   - Header, name, and school text remain legible
   - No elements overlap

## Test Graceful Degradation

1. Temporarily rename the sponsors image:
   ```bash
   mv static/images/sponsors.png static/images/sponsors.png.bak
   ```

2. Generate a PDF again:
   ```bash
   curl -o entrada-no-sponsors.pdf http://localhost:8000/api/entradas/1/pdf
   ```

3. Verify the PDF generates without errors (no sponsors image, but everything else intact)

4. Restore the image:
   ```bash
   mv static/images/sponsors.png.bak static/images/sponsors.png
   ```
