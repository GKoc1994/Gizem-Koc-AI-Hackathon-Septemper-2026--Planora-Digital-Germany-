"""Demo: Bauantragspruefung an einem realistischen Antragsstapel.

Keine PDFs, kein API-Key noetig - zeigt die Pruef-Logik (Regelwerk +
Ampel-Report), die auch beim echten PDF-Lauf greift.

    uv run python demo.py
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from bauantragspruefung.checkliste import laden
from bauantragspruefung.modelle import Bauvorhaben, Dokument, Verfahrensart
from bauantragspruefung.regeln import pruefen
from bauantragspruefung.report import ausgeben

PAUSE = 0.9


def zeile(text: str = "") -> None:
    print(text)
    time.sleep(PAUSE)


zeile("Bauantragspruefung - Vollstaendigkeits- und Formaliencheck vor Einreichung")
zeile("=" * 78)
zeile()
zeile("Eingang: 10 PDFs aus dem Antragsordner 'Familie Schneider'")
zeile("Schritt 1/4  Parsen ........... PDF -> Text (docling)")
zeile("Schritt 2/4  Klassifizieren ... welcher Dokumenttyp? (Claude, mit Sicherheitsangabe)")
zeile("Schritt 3/4  Formalien ........ Datum, Unterschriften, Stammdaten")
zeile("Schritt 4/4  Checkliste ....... NRW-Wohngebaeude, Gebaeudeklasse 3")
zeile()
zeile("Ergebnis:")
zeile()

STICHTAG = date(2026, 9, 21)
checkliste = laden(Path("checkliste/nrw-wohngebaeude.yaml"))

vorhaben = Bauvorhaben(
    bauherr="Familie Schneider",
    gemarkung="Lindenthal", flur="12", flurstueck="345",
    gebaeudeklasse=3, verfahrensart=Verfahrensart.VEREINFACHT,
)

STAMM = {"bauherr": "Familie Schneider", "gemarkung": "Lindenthal",
         "flur": "12", "flurstueck": "345"}


def dok(name, typ, sicherheit=0.95, datum=None, unterzeichner=(), felder=None):
    return Dokument(
        datei=Path(f"antrag/{name}"), typ=typ, typ_sicherheit=sicherheit,
        ausstellungsdatum=datum, unterzeichner=list(unterzeichner),
        felder=felder if felder is not None else dict(STAMM),
    )


dokumente = [
    dok("01_antrag.pdf", "antragsformular", unterzeichner=["bauherr"]),
    dok("02_lageplan.pdf", "lageplan", datum=date(2024, 3, 1),
        unterzeichner=["oeffentlich_bestellter_vermessungsingenieur"],
        felder={**STAMM, "flurstueck": "345/2"}),
    dok("03_grundrisse.pdf", "bauzeichnungen", unterzeichner=["entwurfsverfasser"]),
    dok("04_baubeschreibung.pdf", "baubeschreibung"),
    dok("05_berechnung.pdf", "berechnungen"),
    dok("06_entwaesserung.pdf", "entwaesserung"),
    dok("07_geg.pdf", "waermeschutz"),
    dok("08_stellplaetze.pdf", "stellplatznachweis"),
    dok("09_statistik.pdf", "statistikbogen"),
    dok("10_Scan_2026_04.pdf", "unbekannt", sicherheit=0.2, felder={}),
]

befunde = pruefen(vorhaben, dokumente, checkliste, stichtag=STICHTAG)
ausgeben(vorhaben, dokumente, befunde, checkliste.version)

zeile()
zeile("Ohne dieses Tool waeren mindestens 2 dieser Befunde erst beim Bauamt")
zeile("aufgefallen - nach Wochen Wartezeit, als Nachforderung.")
