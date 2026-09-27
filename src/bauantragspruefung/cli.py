"""Einstiegspunkt: bauantrag-pruefen <ordner-mit-pdfs>"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checkliste import laden
from .extrahieren import extrahieren
from .klassifizieren import klassifizieren
from .modelle import Bauvorhaben, Dokument, Verfahrensart
from .parsen import zu_markdown
from .regeln import einreichbar, pruefen
from .report import ausgeben

STANDARD_CHECKLISTE = Path(__file__).resolve().parents[2] / "checkliste" / "nrw-wohngebaeude.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prueft einen Bauantragsstapel auf Vollstaendigkeit und Formalien."
    )
    parser.add_argument("ordner", type=Path, help="Ordner mit den PDFs des Antrags")
    parser.add_argument("--bauherr", required=True)
    parser.add_argument("--gemarkung", default="")
    parser.add_argument("--flur", default="")
    parser.add_argument("--flurstueck", default="")
    parser.add_argument("--gebaeudeklasse", type=int, default=None)
    parser.add_argument(
        "--verfahren",
        type=Verfahrensart,
        default=Verfahrensart.VEREINFACHT,
        choices=list(Verfahrensart),
    )
    parser.add_argument("--sonderbau", action="store_true")
    parser.add_argument("--checkliste", type=Path, default=STANDARD_CHECKLISTE)
    parser.add_argument("--neu", action="store_true", help="PDF-Cache ignorieren")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pdfs = sorted(args.ordner.glob("*.pdf"))
    if not pdfs:
        print(f"Keine PDFs in {args.ordner}", file=sys.stderr)
        return 2

    checkliste = laden(args.checkliste)
    vorhaben = Bauvorhaben(
        bauherr=args.bauherr,
        gemarkung=args.gemarkung,
        flur=args.flur,
        flurstueck=args.flurstueck,
        gebaeudeklasse=args.gebaeudeklasse,
        verfahrensart=args.verfahren,
        sonderbau=args.sonderbau,
    )

    dokumente: list[Dokument] = []
    for pdf in pdfs:
        print(f"Lese {pdf.name} ...", file=sys.stderr)
        markdown = zu_markdown(pdf, neu=args.neu)

        klasse = klassifizieren(markdown, checkliste)
        dok = Dokument(datei=pdf, typ=klasse.typ, typ_sicherheit=klasse.sicherheit)

        if klasse.typ != "unbekannt":
            formalien = extrahieren(markdown, klasse.typ)
            dok.ausstellungsdatum = formalien.ausstellungsdatum
            dok.unterzeichner = formalien.unterzeichner
            dok.felder = {
                "bauherr": formalien.bauherr,
                "gemarkung": formalien.gemarkung,
                "flur": formalien.flur,
                "flurstueck": formalien.flurstueck,
            }

        dokumente.append(dok)

    befunde = pruefen(vorhaben, dokumente, checkliste)

    if args.json:
        import json

        print(json.dumps([b.model_dump() for b in befunde], indent=2, ensure_ascii=False))
    else:
        ausgeben(vorhaben, dokumente, befunde, checkliste.version)

    return 0 if einreichbar(befunde) else 1


if __name__ == "__main__":
    raise SystemExit(main())
