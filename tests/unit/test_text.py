"""Tests del módulo de normalización de texto."""

from __future__ import annotations

import pytest

from animal.domain.errors import InvalidAnswerError
from animal.domain.text import normalize_animal_name, normalize_question, parse_yes_no


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("y", True),
        ("Yes", True),
        (" s ", True),
        ("SÍ", True),
        ("si", True),
        ("1", True),
        ("verdadero", True),
        ("n", False),
        ("NO", False),
        ("false", False),
        ("0", False),
    ],
)
def test_parse_yes_no_recognises_variants(raw: str, expected: bool) -> None:
    assert parse_yes_no(raw) is expected


@pytest.mark.parametrize("raw", ["", "   ", "maybe", "quizás", "??"])
def test_parse_yes_no_rejects_unknown(raw: str) -> None:
    with pytest.raises(InvalidAnswerError):
        parse_yes_no(raw)


def test_normalize_animal_name_lowercases_and_trims() -> None:
    assert normalize_animal_name("  Caballo  Marino ") == "caballo marino"


def test_normalize_animal_name_rejects_empty() -> None:
    with pytest.raises(InvalidAnswerError):
        normalize_animal_name("   ")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("vuela", "Vuela?"),
        ("vuela?", "Vuela?"),
        ("¿vuela?", "Vuela?"),
        ("  tiene  pelo  ", "Tiene pelo?"),
    ],
)
def test_normalize_question_capitalises_and_adds_mark(raw: str, expected: str) -> None:
    assert normalize_question(raw) == expected


def test_normalize_question_rejects_empty() -> None:
    with pytest.raises(InvalidAnswerError):
        normalize_question("¿?")
