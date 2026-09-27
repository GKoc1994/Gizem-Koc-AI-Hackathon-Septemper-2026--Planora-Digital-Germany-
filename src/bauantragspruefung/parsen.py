"""Schritt 1: PDF/DOCX -> Markdown. Ergebnisse werden gecacht."""

from __future__ import annotations

import hashlib
from pathlib import Path

CACHE = Path(__file__).resolve().parents[2] / "cache"


def _cache_pfad(pdf: Path) -> Path:
    schluessel = hashlib.sha256(pdf.read_bytes()).hexdigest()[:16]
    return CACHE / f"{pdf.stem}-{schluessel}.md"


def zu_markdown(pdf: Path, neu: bool = False) -> str:
    """Konvertiert einen Beleg nach Markdown (inkl. Tabellen).

    Docling laeuft lokal - die Belege verlassen den Rechner nicht.
    """
    pdf = Path(pdf)
    ziel = _cache_pfad(pdf)
    if ziel.exists() and not neu:
        return ziel.read_text(encoding="utf-8")

    from docling.document_converter import DocumentConverter

    ergebnis = DocumentConverter().convert(str(pdf))
    markdown = ergebnis.document.export_to_markdown()

    CACHE.mkdir(exist_ok=True)
    ziel.write_text(markdown, encoding="utf-8")
    return markdown
