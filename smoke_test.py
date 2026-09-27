"""Smoke-Test ohne PDFs und ohne API-Key: prueft Checkliste, Regeln und Report."""

from datetime import date
from pathlib import Path

from bauantragspruefung.checkliste import laden
from bauantragspruefung.modelle import Bauvorhaben, Dokument, Verfahrensart
from bauantragspruefung.regeln import pruefen
from bauantragspruefung.report import ausgeben

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
    # Entwurfsverfasser hat nicht unterschrieben
    dok("01_antrag.pdf", "antragsformular", unterzeichner=["bauherr"]),
    # Lageplan von 2024 -> Frist gerissen, ausserdem abweichendes Flurstueck
    dok("02_lageplan.pdf", "lageplan", datum=date(2024, 3, 1),
        unterzeichner=["oeffentlich_bestellter_vermessungsingenieur"],
        felder={**STAMM, "flurstueck": "345/2"}),
    dok("03_grundrisse.pdf", "bauzeichnungen", unterzeichner=["entwurfsverfasser"]),
    dok("04_baubeschreibung.pdf", "baubeschreibung"),
    dok("05_berechnung.pdf", "berechnungen"),
    # Standsicherheit fehlt komplett (Pflicht ab Gebaeudeklasse 3)
    dok("06_entwaesserung.pdf", "entwaesserung"),
    dok("07_geg.pdf", "waermeschutz"),
    dok("08_stellplaetze.pdf", "stellplatznachweis"),
    dok("09_statistik.pdf", "statistikbogen"),
    # unleserlicher Scan
    dok("10_Scan_2026_04.pdf", "unbekannt", sicherheit=0.2, felder={}),
]

befunde = pruefen(vorhaben, dokumente, checkliste, stichtag=STICHTAG)
ausgeben(vorhaben, dokumente, befunde, checkliste.version)

codes = {b.code for b in befunde}
erwartet = {"FEHLT", "ZU_ALT", "UNTERSCHRIFT_FEHLT", "STAMMDATEN_ABWEICHUNG", "NICHT_ZUGEORDNET"}
fehlend = erwartet - codes
assert not fehlend, f"nicht erkannt: {fehlend}"

# Brandschutz ist kein Sonderbau -> darf NICHT als fehlend gemeldet werden
assert not any(b.punkt == "Brandschutzkonzept" for b in befunde), "Brandschutz faelschlich gefordert"

print("\nOK - alle erwarteten Befunde erkannt:", sorted(codes))
print("OK - Brandschutz korrekt als nicht einschlaegig erkannt")
