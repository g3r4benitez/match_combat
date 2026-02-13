# match_combat Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-29

## Active Technologies
- Python 3.11+ + FastAPI 0.112.0, SQLModel 0.0.22, reportlab >=4.0 (nuevo), segno >=1.6 (nuevo) (003-entrada-pdf)
- PostgreSQL (producción), SQLite (desarrollo) - sin cambios, no se persisten PDFs (003-entrada-pdf)
- Python 3.11+ + FastAPI 0.112.0, reportlab >=4.0, segno >=1.6 (all existing — no new dependencies) (005-pdf-footer-sponsors)
- N/A (no data changes) (005-pdf-footer-sponsors)

- Python 3.11+ + FastAPI 0.112.0, SQLModel 0.0.22, (001-jwt-auth)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 005-pdf-footer-sponsors: Added Python 3.11+ + FastAPI 0.112.0, reportlab >=4.0, segno >=1.6 (all existing — no new dependencies)
- 002-entradas-crud: Added Python 3.11+ + FastAPI 0.112.0, SQLModel 0.0.22
- 003-entrada-pdf: Added Python 3.11+ + FastAPI 0.112.0, SQLModel 0.0.22, reportlab >=4.0 (nuevo), segno >=1.6 (nuevo)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
