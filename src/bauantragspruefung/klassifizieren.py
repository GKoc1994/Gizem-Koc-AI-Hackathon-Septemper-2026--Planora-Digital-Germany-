"""Schritt 2: Welches Dokument ist das?

Beim Bauantrag kommt ein Stapel mit Namen wie Scan_2026_04.pdf an. Erst
muss klar sein, was drin ist - danach kann die Checkliste abgehakt werden.
"""

from __future__ import annotations

import anthropic
from pydantic import BaseModel, Field

from .checkliste import Checkliste

MODELL = "claude-opus-5"
AUSZUG_ZEICHEN = 3000

SYSTEM = """Du ordnest Dokumente aus einem deutschen Bauantrag einem Typ zu.

Regeln:
- Antworte ausschliesslich mit einer der vorgegebenen ids oder "unbekannt".
- Die Sicherheit ist deine ehrliche Selbsteinschaetzung zwischen 0 und 1.
  Rate nicht. Bei einem unleserlichen Scan oder einem Dokument, das zu
  keinem Typ passt, gehoert "unbekannt" mit niedriger Sicherheit hin -
  eine falsche Zuordnung ist schlimmer als eine fehlende.
"""


class Klassifikation(BaseModel):
    typ: str = Field(description="id aus der Liste oder 'unbekannt'")
    sicherheit: float = Field(ge=0.0, le=1.0)
    begruendung: str = Field(description="ein kurzer Satz")


def klassifizieren(
    markdown: str,
    checkliste: Checkliste,
    client: anthropic.Anthropic | None = None,
) -> Klassifikation:
    client = client or anthropic.Anthropic()

    typen = "\n".join(f"- {p.id}: {p.titel}" for p in checkliste.punkte)
    auszug = markdown[:AUSZUG_ZEICHEN]

    antwort = client.messages.parse(
        model=MODELL,
        max_tokens=4000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        output_format=Klassifikation,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Moegliche Typen:\n{typen}\n- unbekannt\n\n"
                    f"Dokumentanfang:\n\n{auszug}"
                ),
            }
        ],
    )
    return antwort.parsed_output
