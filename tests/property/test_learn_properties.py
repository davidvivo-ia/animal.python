"""Propiedades del aprendizaje del árbol."""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from animal.domain.knowledge import (
    KnowledgeTree,
    default_tree,
    learn,
    list_animals,
    walk,
)


def _learn_sequence(tree: KnowledgeTree, plan: list[tuple[str, bool, str, bool]]) -> KnowledgeTree:
    """Aplica una serie de "le enseño un animal nuevo" siguiendo decisiones del jugador."""
    for new_name, swim_answer, question, new_answer in plan:
        # En cada ronda contestamos "nada=swim_answer" y dejamos que el árbol falle.
        result = (
            walk(tree, (swim_answer,))
            if len(_questions_from(tree)) == 1
            else _force_leaf(tree, swim_answer)
        )
        if result.leaf.name == new_name:
            # Acertó: no aprendemos nada, saltamos.
            continue
        tree = learn(
            tree,
            wrong_leaf_path=result.path,
            wrong_leaf_id=result.leaf_id,
            new_animal_name=new_name,
            distinguishing_question=question,
            new_animal_answer=new_answer,
        )
    return tree


def _questions_from(tree: KnowledgeTree) -> list[int]:
    from animal.domain.knowledge import Question

    return [int(i) for i, n in tree.nodes.items() if isinstance(n, Question)]


def _force_leaf(tree: KnowledgeTree, first_answer: bool):
    """Encuentra una hoja siguiendo first_answer en cada bifurcación."""
    from animal.domain.knowledge import Animal, Step

    current = tree.root
    path: list[Step] = []
    while True:
        node = tree.node(current)
        if isinstance(node, Animal):
            from animal.domain.knowledge import WalkResult

            return WalkResult(leaf_id=current, leaf=node, path=tuple(path))
        path.append(Step(node_id=current, answered_yes=first_answer))
        current = node.yes if first_answer else node.no


@given(
    plan=st.lists(
        st.tuples(
            st.text(
                alphabet=st.characters(whitelist_categories=("Ll",)),
                min_size=2,
                max_size=8,
            ),
            st.booleans(),
            st.text(
                alphabet=st.characters(whitelist_categories=("Ll",)),
                min_size=3,
                max_size=10,
            ).map(lambda s: s.capitalize() + "?"),
            st.booleans(),
        ),
        min_size=0,
        max_size=10,
    ),
)
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=60, deadline=None)
def test_learning_never_removes_animals(plan: list[tuple[str, bool, str, bool]]) -> None:
    tree = default_tree()
    before = set(list_animals(tree))
    new_tree = _learn_sequence(tree, plan)
    after = set(list_animals(new_tree))
    assert before <= after


@given(
    plan=st.lists(
        st.tuples(
            st.text(
                alphabet=st.characters(whitelist_categories=("Ll",)),
                min_size=2,
                max_size=8,
            ),
            st.booleans(),
            st.text(
                alphabet=st.characters(whitelist_categories=("Ll",)),
                min_size=3,
                max_size=10,
            ).map(lambda s: s.capitalize() + "?"),
            st.booleans(),
        ),
        min_size=0,
        max_size=8,
    ),
)
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=40, deadline=None)
def test_every_animal_is_reachable(plan: list[tuple[str, bool, str, bool]]) -> None:
    """Toda hoja debe ser alcanzable por algún camino de respuestas."""
    from animal.domain.knowledge import Animal

    tree = _learn_sequence(default_tree(), plan)
    animals_in_tree = {node.name for node in tree.nodes.values() if isinstance(node, Animal)}
    reached: set[str] = set()
    _collect(tree, tree.root, reached)
    assert animals_in_tree == reached


def _collect(tree: KnowledgeTree, node_id: int, acc: set[str]) -> None:
    from animal.domain.knowledge import Animal, NodeId, Question

    node = tree.node(NodeId(node_id))
    if isinstance(node, Animal):
        acc.add(node.name)
        return
    assert isinstance(node, Question)
    _collect(tree, int(node.yes), acc)
    _collect(tree, int(node.no), acc)
