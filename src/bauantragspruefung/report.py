"""Schritt 5: Fehlliste ausgeben."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .modelle import Bauvorhaben, Befund, Dokument, Schwere

FARBE = {Schwere.HOCH: "red", Schwere.MITTEL: "yellow", Schwere.INFO: "cyan"}
AMPEL = {Schwere.HOCH: "ROT", Schwere.MITTEL: "GELB", Schwere.INFO: "INFO"}

HINWEIS = (
    "Arbeitshilfe zur Vollstaendigkeit und zu Formalien. Keine Aussage zur "
    "Genehmigungsfaehigkeit - Plan- und Nachweisinhalte werden nicht geprueft."
)


def _gegenueberstellung(b: Befund) -> str:
    if b.erwartet and b.gefunden:
        return f"{b.erwartet}\n[dim]statt[/] {b.gefunden}"
    return b.erwartet or b.gefunden or "-"


def ausgeben(
    vorhaben: Bauvorhaben,
    dokumente: list[Dokument],
    befunde: list[Befund],
    checkliste_version: str = "",
) -> None:
    console = Console()

    console.print()
    console.print(
        f"[bold]Bauvorhaben[/] {vorhaben.bauherr}  [dim]|[/]  "
        f"Gemarkung {vorhaben.gemarkung or '?'}, Flur {vorhaben.flur or '?'}, "
        f"Flurstueck {vorhaben.flurstueck or '?'}"
    )
    console.print(
        f"[dim]{len(dokumente)} Dokumente  |  Verfahren: {vorhaben.verfahrensart.value}"
        f"  |  Gebaeudeklasse: {vorhaben.gebaeudeklasse or '?'}"
        f"  |  Checkliste: {checkliste_version or '?'}[/]"
    )
    console.print()

    if not befunde:
        console.print("[bold green]Keine Beanstandungen in der Formalienpruefung.[/]")
        console.print(f"[dim]{HINWEIS}[/]")
        return

    tabelle = Table(show_lines=False, header_style="bold")
    tabelle.add_column("", width=5)
    tabelle.add_column("Vorlage", overflow="fold", max_width=24)
    tabelle.add_column("Beanstandung", overflow="fold", min_width=30)
    tabelle.add_column("Erwartet / Gefunden", overflow="fold")
    tabelle.add_column("Datei", style="dim", overflow="fold")

    for b in befunde:
        farbe = FARBE[b.schwere]
        tabelle.add_row(
            f"[{farbe}]{AMPEL[b.schwere]}[/]",
            b.punkt or "-",
            b.text,
            _gegenueberstellung(b),
            b.fundstelle or "-",
        )

    console.print(tabelle)
    console.print()

    anzahl = {s: sum(1 for b in befunde if b.schwere is s) for s in Schwere}
    if anzahl[Schwere.HOCH]:
        console.print(
            f"[bold red]So nicht einreichen[/] - {anzahl[Schwere.HOCH]} fehlende "
            f"Pflichtvorlage(n) bzw. Fristverstoss, {anzahl[Schwere.MITTEL]} zur Pruefung."
        )
    else:
        console.print(
            f"[bold yellow]Einreichbar nach Sichtpruefung[/] - "
            f"{anzahl[Schwere.MITTEL]} Hinweis(e)."
        )
    console.print(f"[dim]{HINWEIS}[/]")
