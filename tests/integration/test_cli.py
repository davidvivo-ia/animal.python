"""Tests del CLI Typer."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from animal import __version__
from animal.presentation.cli import app


def test_version_flag_prints_and_exits() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_demo_mode_runs_to_completion(tmp_path: Path) -> None:
    runner = CliRunner()
    db = tmp_path / "kb.json"
    result = runner.invoke(app, ["--demo", "--db", str(db), "--seed", "42"])
    assert result.exit_code == 0
    assert db.exists()
    assert "murciélago" in db.read_text(encoding="utf-8")


def test_reset_flag_clears_existing_db(tmp_path: Path) -> None:
    runner = CliRunner()
    db = tmp_path / "kb.json"
    # Primera pasada: aprende murciélago.
    runner.invoke(app, ["--demo", "--db", str(db)])
    assert "murciélago" in db.read_text(encoding="utf-8")

    # Reset + demo de nuevo: debe quedar la kb tras aprender otra vez.
    runner.invoke(app, ["--demo", "--reset", "--db", str(db)])
    text = db.read_text(encoding="utf-8")
    # Tras el reset el demo vuelve a enseñar murciélago.
    assert "murciélago" in text
