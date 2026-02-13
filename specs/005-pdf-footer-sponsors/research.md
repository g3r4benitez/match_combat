# Research: PDF Footer Sponsors Image

## Decision 1: Image Placement Strategy

**Decision**: Place the sponsors image at the very bottom of the page (anchored to MARGIN), and shift the QR code upward to make room.

**Rationale**: The current layout positions the QR code at the bottom (`qr_y = MARGIN + 0.3cm`). The sponsors image is a horizontal banner that fits naturally as a page footer. Anchoring it to the bottom margin keeps a consistent footer position regardless of content above.

**Alternatives considered**:
- Place image between QR and text: Rejected — breaks visual flow; QR should be the last functional element before decorative footer.
- Reduce QR size to fit image: Could reduce from 3.5cm to 3.0cm, but not necessary with current calculations — space is sufficient.

## Decision 2: Layout Space Calculation

**Decision**: The sponsors image at full content width (4.4cm) will be ~1.53cm tall. The QR code shifts up by approximately 1.5cm. This leaves adequate space.

**Rationale**:
- Page height: 10cm, Margin: 0.3cm per side → usable: 9.4cm
- Text content from top: header(1.0) + separator(0.5) + nombre(1.0) + escuela(0.8) = 3.3cm → text ends at y ≈ 6.4cm from bottom
- Sponsors image: 0.3cm (margin) to ~1.83cm from bottom (1.53cm height)
- Gap above sponsors: ~0.2cm
- QR (3.5cm): from ~2.03cm to ~5.53cm from bottom
- Gap between QR top and text bottom: 6.4 - 5.53 = 0.87cm — sufficient breathing room

**Alternatives considered**:
- Increase page height: Rejected — would change ticket dimensions which may affect printing.
- Shrink QR to 3.0cm: Not necessary, but available as fallback if additional elements are added later.

## Decision 3: Graceful Degradation

**Decision**: Use a try/except around the image loading. If the file is missing or invalid, log a warning and continue PDF generation without the footer image. No layout changes needed — the QR simply stays in its shifted-up position.

**Rationale**: The spec requires FR-006 (graceful degradation). Since this is a cosmetic element, the PDF should still be functional without sponsors. The QR position is calculated before the image is drawn, so it stays consistent whether or not the image loads.

**Alternatives considered**:
- Check file existence before opening: Less robust — doesn't handle corrupted files or permission issues.
- Move QR back down if image fails: Adds complexity for no user benefit — the shifted QR position is fine either way.

## Decision 4: Image Path Resolution

**Decision**: Use `pathlib.Path` relative to the project root (derived from `ROOT_DIR` in `app/core/config.py`) to construct the absolute path to `static/images/sponsors.png`.

**Rationale**: The project already uses `ROOT_DIR = os.getcwd()` in config.py for path resolution. Using the same root ensures consistency across development and production environments.

**Alternatives considered**:
- Hardcode relative path from service file: Fragile — depends on working directory at runtime.
- Add config variable for image path: Over-engineering for a single static asset per YAGNI principle (Constitution Principle V).
