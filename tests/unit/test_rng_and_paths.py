"""Tests para StdRng y paths."""

from __future__ import annotations

from pathlib import Path

from animal.infrastructure import StdRng, default_db_path


def test_stdrng_is_deterministic_with_seed() -> None:
    a = StdRng(seed=42)
    b = StdRng(seed=42)
    assert a.random() == b.random()
    options = ["uno", "dos", "tres"]
    assert a.choice(options) == b.choice(options)


def test_stdrng_without_seed_returns_floats() -> None:
    rng = StdRng()
    value = rng.random()
    assert 0.0 <= value < 1.0


def test_default_db_path_is_under_user_data(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    path = default_db_path()
    assert path.name == "knowledge.json"
    assert path.parent.exists()
