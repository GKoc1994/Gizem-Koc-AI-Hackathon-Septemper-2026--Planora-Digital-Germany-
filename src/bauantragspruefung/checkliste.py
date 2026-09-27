"""Laedt die Checkliste und entscheidet, welche Punkte Pflicht sind.

Die Pruefregeln stehen bewusst in einer YAML-Datei und nicht im Code:
Bauordnung ist Landesrecht, und die Liste soll ein Architekt gegenlesen
koennen, ohne Python zu verstehen.
"""

from __future__ import annotations

import operator
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from .modelle import Bauvorhaben

OPERATOREN = {
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}


class Bedingung(BaseModel):
    feld: str
    operator: str
    wert: Any

    def trifft_zu(self, vorhaben: Bauvorhaben) -> bool | None:
        """None = nicht entscheidbar, weil das Feld unbekannt ist."""
        ist = getattr(vorhaben, self.feld, None)
        if ist is None:
            return None
        vergleich = OPERATOREN.get(self.operator)
        if vergleich is None:
            raise ValueError(f"Unbekannter Operator in der Checkliste: {self.operator}")
        return vergleich(ist, self.wert)


class Pruefung(BaseModel):
    typ: str
    von: str | None = None
    monate: int | None = None
    felder: list[str] = []


class Pruefpunkt(BaseModel):
    id: str
    titel: str
    quelle: str = ""
    pflicht: Any = "immer"
    pruefungen: list[Pruefung] = []

    def ist_pflicht(self, vorhaben: Bauvorhaben) -> bool | None:
        """True = Pflicht, False = entfaellt, None = nicht entscheidbar."""
        if self.pflicht == "immer":
            return True
        if isinstance(self.pflicht, dict) and "wenn" in self.pflicht:
            return Bedingung(**self.pflicht["wenn"]).trifft_zu(vorhaben)
        return True


class Checkliste(BaseModel):
    version: str
    bundesland: str
    gilt_fuer: str
    punkte: list[Pruefpunkt]

    def nach_id(self, punkt_id: str) -> Pruefpunkt | None:
        return next((p for p in self.punkte if p.id == punkt_id), None)


def laden(pfad: Path) -> Checkliste:
    daten = yaml.safe_load(Path(pfad).read_text(encoding="utf-8"))
    return Checkliste(**daten)
