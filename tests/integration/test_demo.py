"""Test E2E del modo demo headless."""

from __future__ import annotations

import io
from pathlib import Path

from rich.console import Console

from animal.application import GameSession
from animal.infrastructure.repository import JsonRepository
from animal.presentation.demo import DEMO_SCRIPT
from animal.presentation.headless import run_repl


def test_demo_completes_and_persists(tmp_path: Path) -> None:
    repo = JsonRepository(path=tmp_path / "kb.json")
    session = GameSession.open(repo)

    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=80)
    code = run_repl(session, console=console, inputs=DEMO_SCRIPT)

    assert code == 0
    out = buffer.getvalue()
    # El guion acierta con pez y aprende murciélago.
    assert "Bien" in out or "bien" in out.lower()
    assert "murciélago" in session.known_animals()
    # Persistencia ocurrió.
    assert (tmp_path / "kb.json").exists()
