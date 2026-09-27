# Bauantragsprüfung

Prüft einen Bauantragsstapel **vor der Einreichung** auf Vollständigkeit und
Formalien — also auf das, was bei Bauämtern die häufigsten Nachforderungen
auslöst.

> **Was das Tool nicht tut:** keine inhaltliche Planprüfung. Abstandsflächen,
> GRZ/GFZ, Brandschutzkonzepte, Standsicherheit — nichts davon wird bewertet.
> Es werden keine Maße aus Bauzeichnungen gelesen. Das Ergebnis ist eine
> Arbeitshilfe, keine Aussage zur Genehmigungsfähigkeit.

## Pipeline

```
PDFs  →  [1] Parsen  →  [2] Klassifizieren  →  [3] Formalien  →  [4] Checkliste  →  [5] Fehlliste
         docling         welches Dokument?      Datum, Unterschrift   abhaken        Ampel
```

Wie bei der Rechnungsprüfung gilt: **Claude klassifiziert und extrahiert,
es urteilt nicht.** Ob eine Vorlage fehlt oder eine Frist gerissen ist,
entscheidet [regeln.py](src/bauantragspruefung/regeln.py) in reinem Python.

| Datei | Aufgabe |
|---|---|
| `parsen.py` | PDF → Markdown via docling, lokal, mit Cache |
| `klassifizieren.py` | Welcher Dokumenttyp? Mit ehrlicher Sicherheitsangabe |
| `extrahieren.py` | Ausstellungsdatum, Unterschriften, Stammdaten |
| `checkliste.py` | Lädt die YAML-Checkliste, wertet Pflicht-Bedingungen aus |
| `regeln.py` | Die vier Prüfungsarten, deterministisch |
| `report.py` | Ampel-Tabelle im Terminal |

## Die Checkliste ist eine Datei, kein Code

[checkliste/nrw-wohngebaeude.yaml](checkliste/nrw-wohngebaeude.yaml) enthält
die Pflichtvorlagen. Das hat drei Gründe: Bauordnung ist Landesrecht, die
Pflichtliste hängt vom Vorhaben ab (Gebäudeklasse, Verfahrensart, Sonderbau),
und eine YAML-Datei kann ein Architekt gegenlesen — dein Python-Code nicht.

> ⚠️ **Die mitgelieferte Checkliste ist ein Entwurf.** Die Dokumenttypen sind
> die üblichen Bauvorlagen, aber **jedes `quelle:`-Feld ist ein TODO** und jede
> Frist ist geschätzt. Vor dem ersten echten Einsatz gegen die aktuelle
> BauPrüfVO NRW und BauO NRW füllen und von einer bauvorlageberechtigten
> Person gegenlesen lassen.

### Die vier Prüfungsarten

| Typ | Prüft | Ampel |
|---|---|---|
| `vorhanden` | Ist die Pflichtvorlage im Stapel? | rot |
| `nicht_aelter_als` | Ausstellungsdatum innerhalb der Frist | rot |
| `unterschrift` | Ist die geforderte Rolle unterzeichnet? | gelb |
| `konsistent_mit` | Stammdaten gleich wie im Vorhaben? | gelb |

Eine Pflicht-Bedingung sieht so aus — bewusst als Struktur, nicht als
auswertbarer Ausdruck:

```yaml
pflicht:
  wenn:
    feld: gebaeudeklasse
    operator: ">="
    wert: 3
```

Fehlt das Feld im Vorhaben, meldet das Tool `PFLICHT_UNKLAR` statt zu raten.

## Installation

```bash
cd ~/Claude/bauantrag && uv sync --extra pdf
```

Der Extra `pdf` zieht docling samt PyTorch — beim ersten Mal ein paar Minuten
und einige GB. Ohne den Extra läuft alles außer dem PDF-Parsing.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Benutzung

```bash
uv run bauantrag-pruefen antrag/ --bauherr "Familie Schneider" --gemarkung Lindenthal --flur 12 --flurstueck 345 --gebaeudeklasse 3
```

Exit-Code 0 = keine roten Befunde, 1 = so nicht einreichen.
`--json` gibt maschinenlesbar aus, `--neu` ignoriert den PDF-Cache,
`--checkliste` nimmt eine andere Checkliste.

Logik testen ohne PDFs und ohne API-Key:

```bash
uv run python smoke_test.py
```

## Befundcodes

| Code | Ampel | Bedeutung |
|---|---|---|
| `FEHLT` | rot | Pflichtvorlage nicht im Stapel |
| `ZU_ALT` | rot | Frist gerissen |
| `UNTERSCHRIFT_FEHLT` | gelb | Geforderte Rolle hat nicht unterzeichnet |
| `STAMMDATEN_ABWEICHUNG` | gelb | Bauherr/Flurstück weicht ab |
| `ZUORDNUNG_UNSICHER` | gelb | Klassifikation unter 0,75 — sichten |
| `NICHT_ZUGEORDNET` | gelb | Dokument passt zu keinem Punkt |
| `DATUM_UNBEKANNT` | gelb | Kein Ausstellungsdatum gefunden |
| `PFLICHT_UNKLAR` | gelb | Angabe zum Vorhaben fehlt |

## Grenzen (Stand jetzt)

- **Die Checkliste ist ungeprüft** — siehe Warnung oben. Das ist die größte
  offene Baustelle, und sie ist Recherche, nicht Code.
- **Nur ein Dokument pro Datei.** Ein Sammel-PDF mit Antrag + Lageplan +
  Baubeschreibung wird als ein Dokument klassifiziert und fällt durch.
  Bei echten Stapeln häufig — dann muss vorher gesplittet werden.
- **Klassifikation liest nur die ersten 3000 Zeichen.** Reicht für Formulare
  mit Kopf, nicht unbedingt für Scans, bei denen oben nichts steht.
- **Keine OCR-Kontrolle.** Wenn docling aus einem schiefen Scan Unsinn macht,
  merkt das Tool das nicht — es sieht dann nur ein schwer klassifizierbares
  Dokument. Die Sicherheitsangabe federt das teilweise ab.
- **Unterschriftenprüfung ist Textprüfung**, keine Bilderkennung. Erkannt wird
  ein ausgefülltes Unterschriftsfeld im Text, nicht ein Krakel im Scan.
- **Das eigentliche Risiko ist Schritt 2.** Wenn die Klassifikation bei echten
  Scans nicht trägt, trägt das ganze Projekt nicht. Das zuerst messen.
