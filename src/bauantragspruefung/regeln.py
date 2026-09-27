"""Schritt 4: Checkliste abhaken - deterministisch, ohne LLM.

Wie bei der Rechnungspruefung gilt: Das Modell extrahiert, es urteilt nicht.
Ob ein Nachweis fehlt oder eine Frist gerissen ist, entscheidet Python.
"""

from __future__ import annotations

import re
from datetime import date

from .checkliste import Checkliste, Pruefpunkt, Pruefung
from .modelle import Bauvorhaben, Befund, Dokument, Schwere

SICHERHEIT_SCHWELLE = 0.75


def _normalisieren(wert: str) -> str:
    """Flur 12 / flur12 / FLUR-12 -> flur12. Fuer den Konsistenzabgleich."""
    return re.sub(r"[\s\-_.,/]", "", wert).lower()


def _dokumente_zu(punkt: Pruefpunkt, dokumente: list[Dokument]) -> list[Dokument]:
    return [d for d in dokumente if d.typ == punkt.id]


def _vorhanden(punkt: Pruefpunkt, treffer: list[Dokument]) -> list[Befund]:
    if not treffer:
        return [
            Befund(
                code="FEHLT",
                schwere=Schwere.HOCH,
                text="Pflichtvorlage fehlt im Stapel",
                punkt=punkt.titel,
                quelle=punkt.quelle,
            )
        ]

    unsicher = [d for d in treffer if d.typ_sicherheit < SICHERHEIT_SCHWELLE]
    if len(unsicher) == len(treffer):
        return [
            Befund(
                code="ZUORDNUNG_UNSICHER",
                schwere=Schwere.MITTEL,
                text="Dokument zugeordnet, aber die Zuordnung ist unsicher - bitte sichten",
                punkt=punkt.titel,
                quelle=punkt.quelle,
                gefunden=", ".join(d.datei.name for d in unsicher),
            )
        ]
    return []


def _nicht_aelter_als(
    punkt: Pruefpunkt, pruefung: Pruefung, treffer: list[Dokument], stichtag: date
) -> list[Befund]:
    befunde = []
    for dok in treffer:
        if dok.ausstellungsdatum is None:
            befunde.append(
                Befund(
                    code="DATUM_UNBEKANNT",
                    schwere=Schwere.MITTEL,
                    text="Kein Ausstellungsdatum gefunden - Frist nicht pruefbar",
                    punkt=punkt.titel,
                    quelle=punkt.quelle,
                    fundstelle=dok.datei.name,
                )
            )
            continue

        alter_monate = (stichtag.year - dok.ausstellungsdatum.year) * 12 + (
            stichtag.month - dok.ausstellungsdatum.month
        )
        if alter_monate > pruefung.monate:
            befunde.append(
                Befund(
                    code="ZU_ALT",
                    schwere=Schwere.HOCH,
                    text=f"Aelter als {pruefung.monate} Monate",
                    punkt=punkt.titel,
                    quelle=punkt.quelle,
                    erwartet=f"hoechstens {pruefung.monate} Monate alt",
                    gefunden=f"{dok.ausstellungsdatum} ({alter_monate} Monate)",
                    fundstelle=dok.datei.name,
                )
            )
    return befunde


def _unterschrift(
    punkt: Pruefpunkt, pruefung: Pruefung, treffer: list[Dokument]
) -> list[Befund]:
    if any(pruefung.von in d.unterzeichner for d in treffer):
        return []
    return [
        Befund(
            code="UNTERSCHRIFT_FEHLT",
            schwere=Schwere.MITTEL,
            text=f"Unterschrift fehlt: {pruefung.von.replace('_', ' ')}",
            punkt=punkt.titel,
            quelle=punkt.quelle,
            erwartet=pruefung.von,
            gefunden=", ".join(sorted({u for d in treffer for u in d.unterzeichner})) or "keine",
            fundstelle=", ".join(d.datei.name for d in treffer),
        )
    ]


def _konsistent_mit(
    punkt: Pruefpunkt, pruefung: Pruefung, treffer: list[Dokument], vorhaben: Bauvorhaben
) -> list[Befund]:
    """Stammdaten im Dokument gegen die Stammdaten des Vorhabens."""
    befunde = []
    for dok in treffer:
        for feld in pruefung.felder:
            im_dokument = (dok.felder.get(feld) or "").strip()
            im_vorhaben = (getattr(vorhaben, feld, "") or "").strip()
            if not im_dokument or not im_vorhaben:
                continue
            if _normalisieren(im_dokument) != _normalisieren(im_vorhaben):
                befunde.append(
                    Befund(
                        code="STAMMDATEN_ABWEICHUNG",
                        schwere=Schwere.MITTEL,
                        text=f"'{feld}' weicht vom Vorhaben ab - haeufiger Nachforderungsgrund",
                        punkt=punkt.titel,
                        quelle=punkt.quelle,
                        erwartet=im_vorhaben,
                        gefunden=im_dokument,
                        fundstelle=dok.datei.name,
                    )
                )
    return befunde


def pruefen(
    vorhaben: Bauvorhaben,
    dokumente: list[Dokument],
    checkliste: Checkliste,
    stichtag: date | None = None,
) -> list[Befund]:
    """Haekt die Checkliste gegen den Stapel ab."""
    stichtag = stichtag or date.today()
    befunde: list[Befund] = []

    for punkt in checkliste.punkte:
        pflicht = punkt.ist_pflicht(vorhaben)

        if pflicht is None:
            befunde.append(
                Befund(
                    code="PFLICHT_UNKLAR",
                    schwere=Schwere.MITTEL,
                    text="Ob diese Vorlage Pflicht ist, haengt von Angaben ab, die fehlen",
                    punkt=punkt.titel,
                    quelle=punkt.quelle,
                )
            )
            continue
        if pflicht is False:
            continue

        treffer = _dokumente_zu(punkt, dokumente)
        fehlt = _vorhanden(punkt, treffer)
        befunde.extend(fehlt)
        if not treffer:
            continue  # ohne Dokument sind die uebrigen Pruefungen sinnlos

        for pruefung in punkt.pruefungen:
            if pruefung.typ == "vorhanden":
                continue
            if pruefung.typ == "nicht_aelter_als":
                befunde.extend(_nicht_aelter_als(punkt, pruefung, treffer, stichtag))
            elif pruefung.typ == "unterschrift":
                befunde.extend(_unterschrift(punkt, pruefung, treffer))
            elif pruefung.typ == "konsistent_mit":
                befunde.extend(_konsistent_mit(punkt, pruefung, treffer, vorhaben))
            else:
                raise ValueError(f"Unbekannte Pruefungsart in der Checkliste: {pruefung.typ}")

    # Dokumente, die zu keinem Checklistenpunkt gehoeren
    bekannte = {p.id for p in checkliste.punkte}
    for dok in dokumente:
        if dok.typ is None or dok.typ == "unbekannt" or dok.typ not in bekannte:
            befunde.append(
                Befund(
                    code="NICHT_ZUGEORDNET",
                    schwere=Schwere.MITTEL,
                    text="Dokument konnte keinem Checklistenpunkt zugeordnet werden",
                    fundstelle=dok.datei.name,
                )
            )

    reihenfolge = {Schwere.HOCH: 0, Schwere.MITTEL: 1, Schwere.INFO: 2}
    return sorted(befunde, key=lambda b: reihenfolge[b.schwere])


def einreichbar(befunde: list[Befund]) -> bool:
    return not any(b.schwere is Schwere.HOCH for b in befunde)
