"""Schritt 3: Formalien aus einem klassifizierten Dokument ziehen."""

from __future__ import annotations

from datetime import date

import anthropic
from pydantic import BaseModel, Field

MODELL = "claude-opus-5"

SYSTEM = """Du liest Formalien aus deutschen Bauantragsunterlagen aus.

Regeln:
- Erfinde nichts. Was nicht im Dokument steht, bleibt leer bzw. null.
- Eine Unterschriftsrolle zaehlt nur als unterzeichnet, wenn dort tatsaechlich
  etwas eingetragen ist. Ein leeres Unterschriftsfeld ist nicht unterzeichnet.
- Stammdaten exakt so uebernehmen, wie sie dastehen - auch bei abweichender
  Schreibweise. Vereinheitliche nichts, gerade Abweichungen sind relevant.
"""


class Formalien(BaseModel):
    ausstellungsdatum: date | None = Field(
        default=None, description="Datum der Ausstellung/Erstellung, nicht das Druckdatum"
    )
    unterzeichner: list[str] = Field(
        default_factory=list,
        description=(
            "Rollen mit ausgefuelltem Unterschriftsfeld. Erlaubt: bauherr, "
            "entwurfsverfasser, nachweisberechtigt_standsicherheit, "
            "oeffentlich_bestellter_vermessungsingenieur, sonstige"
        ),
    )
    bauherr: str = ""
    gemarkung: str = ""
    flur: str = ""
    flurstueck: str = ""


def extrahieren(
    markdown: str,
    dokumenttyp: str,
    client: anthropic.Anthropic | None = None,
) -> Formalien:
    client = client or anthropic.Anthropic()

    antwort = client.messages.parse(
        model=MODELL,
        max_tokens=8000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        output_format=Formalien,
        messages=[
            {
                "role": "user",
                "content": f"Dokumenttyp: {dokumenttyp}\n\n{markdown}",
            }
        ],
    )
    return antwort.parsed_output
