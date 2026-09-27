"""Datenmodelle fuer Bauvorhaben, Dokumente und Befunde."""

from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class Verfahrensart(str, Enum):
    FREISTELLUNG = "freistellung"
    VEREINFACHT = "vereinfachtes_verfahren"
    VOLL = "vollverfahren"


class Bauvorhaben(BaseModel):
    """Die Stammdaten des Vorhabens. Steuern, welche Vorlagen Pflicht sind."""

    bauherr: str
    gemarkung: str = ""
    flur: str = ""
    flurstueck: str = ""
    gebaeudeklasse: int | None = None
    verfahrensart: Verfahrensart = Verfahrensart.VEREINFACHT
    sonderbau: bool = False


class Dokument(BaseModel):
    """Ein Dokument aus dem Antragsstapel, nach Schritt 2 und 3."""

    datei: Path
    typ: str | None = Field(default=None, description="id aus der Checkliste, None = unbekannt")
    typ_sicherheit: float = Field(default=0.0, description="0..1, Selbsteinschaetzung der Klassifikation")
    ausstellungsdatum: date | None = None
    unterzeichner: list[str] = Field(
        default_factory=list,
        description="Rollen mit ausgefuellter Unterschrift, z.B. bauherr, entwurfsverfasser",
    )
    felder: dict[str, str] = Field(
        default_factory=dict,
        description="Stammdaten wie im Dokument geschrieben, fuer den Konsistenzabgleich",
    )
    seiten: int | None = None


class Schwere(str, Enum):
    HOCH = "hoch"      # Antrag so nicht einreichen
    MITTEL = "mittel"  # pruefen
    INFO = "info"


class Befund(BaseModel):
    code: str
    schwere: Schwere
    text: str
    punkt: str | None = Field(default=None, description="Titel des Checklistenpunkts")
    quelle: str | None = None
    erwartet: str | None = None
    gefunden: str | None = None
    fundstelle: str | None = None
