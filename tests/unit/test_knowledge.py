"""Tests del árbol de conocimiento."""

from __future__ import annotations

import pytest

from animal.domain.errors import CorruptedKnowledgeBaseError
from animal.domain.knowledge import (
    Animal,
    KnowledgeTree,
    NodeId,
    Question,
    default_tree,
    learn,
    list_animals,
    walk,
)


def test_default_tree_has_fish_and_bird() -> None:
    tree = default_tree()
    assert set(list_animals(tree)) == {"pez", "ave"}


def test_walk_to_fish() -> None:
    tree = default_tree()
    result = walk(tree, (True,))
    assert result.leaf.name == "pez"
    assert len(result.path) == 1
    assert result.path[0].answered_yes is True


def test_walk_to_bird() -> None:
    tree = default_tree()
    result = walk(tree, (False,))
    assert result.leaf.name == "ave"


def test_walk_short_answers_raises() -> None:
    tree = default_tree()
    with pytest.raises(CorruptedKnowledgeBaseError):
        walk(tree, ())


def test_learn_inserts_new_animal_under_correct_branch() -> None:
    tree = default_tree()
    result = walk(tree, (True,))  # llega a "pez"

    new_tree = learn(
        tree,
        wrong_leaf_path=result.path,
        wrong_leaf_id=result.leaf_id,
        new_animal_name="delfín",
        distinguishing_question="Es mamífero?",
        new_animal_answer=True,
    )

    assert set(list_animals(new_tree)) == {"pez", "ave", "delfín"}

    # En el nuevo árbol, contestando "nada=sí, mamífero=sí" debe salir delfín.
    dolphin_result = walk(new_tree, (True, True))
    assert dolphin_result.leaf.name == "delfín"

    # "nada=sí, mamífero=no" debe seguir saliendo pez.
    fish_result = walk(new_tree, (True, False))
    assert fish_result.leaf.name == "pez"

    # "nada=no" sigue siendo ave (camino intacto).
    bird_result = walk(new_tree, (False,))
    assert bird_result.leaf.name == "ave"


def test_learn_with_new_answer_negative_swaps_branches() -> None:
    tree = default_tree()
    result = walk(tree, (False,))  # llega a "ave"

    new_tree = learn(
        tree,
        wrong_leaf_path=result.path,
        wrong_leaf_id=result.leaf_id,
        new_animal_name="murciélago",
        distinguishing_question="Tiene plumas?",
        new_animal_answer=False,
    )

    # murciélago se alcanza diciendo "nada=no, plumas=no".
    bat = walk(new_tree, (False, False))
    assert bat.leaf.name == "murciélago"
    bird = walk(new_tree, (False, True))
    assert bird.leaf.name == "ave"


def test_learn_does_not_mutate_original_tree() -> None:
    tree = default_tree()
    original_animals = list_animals(tree)
    result = walk(tree, (True,))
    learn(
        tree,
        wrong_leaf_path=result.path,
        wrong_leaf_id=result.leaf_id,
        new_animal_name="delfín",
        distinguishing_question="Es mamífero?",
        new_animal_answer=True,
    )
    assert list_animals(tree) == original_animals


def test_knowledgetree_rejects_root_outside_nodes() -> None:
    with pytest.raises(CorruptedKnowledgeBaseError):
        KnowledgeTree(nodes={NodeId(1): Animal(name="x")}, root=NodeId(99))


def test_knowledgetree_rejects_inconsistent_next_id() -> None:
    nodes = {NodeId(1): Animal(name="x")}
    with pytest.raises(CorruptedKnowledgeBaseError):
        KnowledgeTree(nodes=nodes, root=NodeId(1), next_id=NodeId(1))


def test_node_lookup_unknown_id_raises() -> None:
    tree = default_tree()
    with pytest.raises(CorruptedKnowledgeBaseError):
        tree.node(NodeId(999))


def test_corrupted_walk_when_question_points_nowhere() -> None:
    nodes = {
        NodeId(1): Animal(name="pez"),
        NodeId(2): Question(text="¿?", yes=NodeId(1), no=NodeId(99)),
    }
    with pytest.raises(CorruptedKnowledgeBaseError):
        tree = KnowledgeTree(nodes=nodes, root=NodeId(2), next_id=NodeId(3))
        walk(tree, (False,))
