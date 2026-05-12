"""Tests del repositorio JSON: round-trip y manejo de errores."""

from __future__ import annotations

from pathlib import Path

import pytest

from animal.domain import KnowledgeTree, default_tree, list_animals
from animal.domain.errors import CorruptedKnowledgeBaseError, KnowledgeBaseVersionError
from animal.domain.knowledge import learn, walk
from animal.infrastructure.repository import JsonRepository


def _learn_a_few(tree: KnowledgeTree) -> KnowledgeTree:
    r1 = walk(tree, (True,))
    tree = learn(
        tree,
        wrong_leaf_path=r1.path,
        wrong_leaf_id=r1.leaf_id,
        new_animal_name="delfín",
        distinguishing_question="Es mamífero?",
        new_animal_answer=True,
    )
    r2 = walk(tree, (False,))
    return learn(
        tree,
        wrong_leaf_path=r2.path,
        wrong_leaf_id=r2.leaf_id,
        new_animal_name="murciélago",
        distinguishing_question="Tiene plumas?",
        new_animal_answer=False,
    )


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    repo = JsonRepository(path=tmp_path / "kb.json")
    tree = _learn_a_few(default_tree())
    repo.save(tree)

    repo2 = JsonRepository(path=tmp_path / "kb.json")
    loaded = repo2.load()
    assert list_animals(loaded) == list_animals(tree)


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    repo = JsonRepository(path=tmp_path / "missing.json")
    tree = repo.load()
    assert list_animals(tree) == ("ave", "pez")


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("not json", encoding="utf-8")
    repo = JsonRepository(path=path)
    with pytest.raises(CorruptedKnowledgeBaseError):
        repo.load()


def test_load_wrong_version_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad_version.json"
    path.write_text(
        '{"version": 99, "root": {"kind": "animal", "name": "x"}}',
        encoding="utf-8",
    )
    repo = JsonRepository(path=path)
    with pytest.raises(KnowledgeBaseVersionError):
        repo.load()


def test_save_is_atomic(tmp_path: Path) -> None:
    path = tmp_path / "kb.json"
    repo = JsonRepository(path=path)
    repo.save(default_tree())
    # Tras escribir, no debe quedar ningún tmp residual.
    siblings = list(path.parent.iterdir())
    assert siblings == [path]
