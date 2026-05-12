"""Tests específicos de ramas en el REPL headless."""

from __future__ import annotations

import io
from pathlib import Path

from rich.console import Console

from animal.application import GameSession
from animal.infrastructure.repository import JsonRepository
from animal.presentation.headless import run_repl


def _run(inputs: list[str], tmp_path: Path) -> tuple[int, str, GameSession]:
    repo = JsonRepository(path=tmp_path / "kb.json")
    session = GameSession.open(repo)
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=80)
    code = run_repl(session, console=console, inputs=inputs)
    return code, buffer.getvalue(), session


def test_quit_immediately(tmp_path: Path) -> None:
    code, out, _ = _run(["salir"], tmp_path)
    assert code == 0
    assert "Hasta luego" in out


def test_list_command_shows_known_animals(tmp_path: Path) -> None:
    code, out, _ = _run(["list", "salir"], tmp_path)
    assert code == 0
    assert "pez" in out and "ave" in out


def test_invalid_then_no(tmp_path: Path) -> None:
    code, out, _ = _run(["quizás", "no", "salir"], tmp_path)
    assert code == 0
    assert "sí/no" in out.lower() or "responde" in out.lower()


def test_negative_at_top_level_skips_round(tmp_path: Path) -> None:
    code, _, session = _run(["no", "salir"], tmp_path)
    assert code == 0
    assert session.stats.rounds_played == 0


def test_invalid_yes_no_inside_round_loops_until_valid(tmp_path: Path) -> None:
    code, _, session = _run(["sí", "quizá", "sí", "sí", "salir"], tmp_path)
    assert code == 0
    # Llegó a pez y lo confirmó.
    assert session.stats.correct_guesses == 1


def test_empty_text_inside_round_loops(tmp_path: Path) -> None:
    inputs = [
        "sí",  # ¿estás pensando?
        "no",  # llega a ave
        "no",  # no es ave
        "",  # nombre vacío → debe pedir otra vez
        "loro",  # nombre válido
        "tiene plumas",
        "sí",
        "salir",
    ]
    code, _, session = _run(inputs, tmp_path)
    assert code == 0
    assert "loro" in session.known_animals()


def test_eof_in_round_exits_cleanly(tmp_path: Path) -> None:
    # Solo dos líneas: empezamos y luego se acaba el input.
    code, _, _ = _run(["sí"], tmp_path)
    assert code == 0
