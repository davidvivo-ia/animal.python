"""Tests de la GameSession."""

from __future__ import annotations

import pytest

from animal.application.session import GameSession
from animal.domain import Animal, Question
from animal.domain.errors import AnimalError
from animal.infrastructure.repository import InMemoryRepository


def test_open_loads_tree_from_repository() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    assert session.known_animals() == ("ave", "pez")


def test_round_to_fish_and_confirm_persists() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    node = session.start_round()
    assert isinstance(node, Question)
    leaf = session.answer(yes=True)
    assert isinstance(leaf, Animal)
    assert leaf.name == "pez"
    session.confirm_correct()
    assert repo.save_calls == 1
    assert session.stats.correct_guesses == 1


def test_teaching_new_animal_persists_and_lists() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    session.start_round()
    session.answer(yes=False)  # llega a "ave"
    session.teach_new_animal(
        new_animal_raw="murciélago",
        distinguishing_question_raw="¿tiene plumas?",
        new_animal_answers_yes=False,
    )
    assert "murciélago" in session.known_animals()
    assert repo.save_calls == 1
    assert session.stats.animals_learned == 1


def test_answer_without_round_raises() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    with pytest.raises(AnimalError):
        session.answer(yes=True)


def test_reset_replaces_tree() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    session.start_round()
    session.answer(yes=False)
    session.teach_new_animal(
        new_animal_raw="murciélago",
        distinguishing_question_raw="¿tiene plumas?",
        new_animal_answers_yes=False,
    )
    assert "murciélago" in session.known_animals()
    session.reset_to_default()
    assert session.known_animals() == ("ave", "pez")
