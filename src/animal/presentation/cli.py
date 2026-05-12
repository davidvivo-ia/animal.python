"""CLI Typer del juego ANIMAL.

Punto de entrada único. Elige entre TUI Textual, modo headless REPL, o
modo demo según las flags.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from animal import __version__
from animal.application import GameSession
from animal.infrastructure import JsonRepository, StdRng, default_db_path
from animal.presentation.demo import DEMO_SCRIPT
from animal.presentation.headless import run_repl

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    help="ANIMAL — reconstrucción 2026 del clásico de Creative Computing (1973).",
)


def _version_callback(show: bool) -> None:
    if show:
        typer.echo(f"animal {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    db: Path = typer.Option(  # noqa: B008
        None,
        "--db",
        help="Ruta al fichero JSON de conocimiento.",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Descarta el conocimiento guardado y empieza desde el árbol por defecto.",
    ),
    seed: int = typer.Option(
        None,
        "--seed",
        help="Semilla RNG para sesiones reproducibles.",
    ),
    headless: bool = typer.Option(
        False,
        "--headless",
        help="Modo REPL sin TUI Textual (útil sobre SSH o pipes).",
    ),
    demo: bool = typer.Option(
        False,
        "--demo",
        help="Reproduce un guion determinista y termina (no requiere terminal interactivo).",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Imprime la versión y sale.",
    ),
) -> None:
    """Lanza el juego en el modo elegido."""
    path = db or default_db_path()
    repository = JsonRepository(path=path)
    session = GameSession.open(repository)
    # `--demo` siempre parte de un árbol limpio para ser determinista.
    if reset or demo:
        session.reset_to_default()
    # RNG inyectado por consistencia; v1.0 lo usa para futuras mejoras.
    _ = StdRng(seed=seed)

    if demo:
        console = Console(force_terminal=True, soft_wrap=True)
        sys.exit(run_repl(session, console=console, inputs=DEMO_SCRIPT))
    if headless:
        sys.exit(run_repl(session))

    # Modo por defecto: TUI Textual.
    from animal.presentation.tui import AnimalApp

    AnimalApp(session=session).run()
