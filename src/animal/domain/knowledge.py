"""Árbol de conocimiento del juego ANIMAL.

Modelado como árbol persistente inmutable: cada operación de aprendizaje
devuelve un nuevo ``KnowledgeTree``. Los nodos se identifican por
``NodeId`` enteros estables.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import NewType

from animal.domain.errors import CorruptedKnowledgeBaseError

NodeId = NewType("NodeId", int)

# Camino recorrido = lista de (id-de-pregunta, respuesta-tomada).
type Answer = bool


@dataclass(frozen=True, slots=True)
class Animal:
    """Hoja del árbol: un animal concreto."""

    name: str


@dataclass(frozen=True, slots=True)
class Question:
    """Nodo interno: una pregunta sí/no con dos hijos."""

    text: str
    yes: NodeId
    no: NodeId


type Node = Animal | Question


@dataclass(frozen=True, slots=True)
class Step:
    """Un paso del recorrido: la pregunta visitada y la respuesta dada."""

    node_id: NodeId
    answered_yes: Answer


@dataclass(frozen=True, slots=True)
class WalkResult:
    """Resultado de bajar por el árbol hasta una hoja."""

    leaf_id: NodeId
    leaf: Animal
    path: tuple[Step, ...]


@dataclass(frozen=True, slots=True)
class KnowledgeTree:
    """Conjunto inmutable de nodos enlazados por id, con raíz fija."""

    nodes: Mapping[NodeId, Node]
    root: NodeId
    next_id: NodeId = field(default=NodeId(0))

    def __post_init__(self) -> None:
        # Bloqueamos en MappingProxyType para inmutabilidad estructural real.
        if not isinstance(self.nodes, MappingProxyType):
            object.__setattr__(self, "nodes", MappingProxyType(dict(self.nodes)))
        if self.root not in self.nodes:
            raise CorruptedKnowledgeBaseError(f"raíz {self.root} no existe en el mapa de nodos")
        computed_next = max(self.nodes.keys()) + 1 if self.nodes else 0
        if self.next_id == 0:
            object.__setattr__(self, "next_id", NodeId(computed_next))
        elif self.next_id < computed_next:
            raise CorruptedKnowledgeBaseError(
                f"next_id={self.next_id} es menor que el id máximo presente ({computed_next - 1})",
            )

    def node(self, node_id: NodeId) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise CorruptedKnowledgeBaseError(f"id de nodo desconocido: {node_id}") from exc


def default_tree() -> KnowledgeTree:
    """Devuelve el árbol inicial homenaje al BASIC: peces vs aves."""
    fish_id = NodeId(1)
    bird_id = NodeId(2)
    root_id = NodeId(3)
    nodes: dict[NodeId, Node] = {
        fish_id: Animal(name="pez"),
        bird_id: Animal(name="ave"),
        root_id: Question(text="¿Nada?", yes=fish_id, no=bird_id),
    }
    return KnowledgeTree(nodes=nodes, root=root_id, next_id=NodeId(4))


def walk(tree: KnowledgeTree, answers: tuple[Answer, ...]) -> WalkResult:
    """Recorre el árbol consumiendo respuestas hasta llegar a una hoja.

    Args:
        tree: árbol de conocimiento.
        answers: secuencia de respuestas precomputadas (modo demo/tests).

    Returns:
        ``WalkResult`` con la hoja alcanzada y el camino seguido.

    Raises:
        CorruptedKnowledgeBaseError: si se agotan las respuestas antes
            de alcanzar una hoja, o si el árbol referencia un id
            desconocido.
    """
    current_id = tree.root
    path: list[Step] = []
    cursor = 0
    while True:
        node = tree.node(current_id)
        if isinstance(node, Animal):
            return WalkResult(leaf_id=current_id, leaf=node, path=tuple(path))
        if cursor >= len(answers):
            raise CorruptedKnowledgeBaseError(
                "se agotaron las respuestas antes de alcanzar una hoja",
            )
        answer = answers[cursor]
        path.append(Step(node_id=current_id, answered_yes=answer))
        current_id = node.yes if answer else node.no
        cursor += 1


def learn(
    tree: KnowledgeTree,
    *,
    wrong_leaf_path: tuple[Step, ...],
    wrong_leaf_id: NodeId,
    new_animal_name: str,
    distinguishing_question: str,
    new_animal_answer: Answer,
) -> KnowledgeTree:
    """Inserta un nuevo animal sustituyendo una hoja por una pregunta.

    Args:
        tree: árbol antes de aprender.
        wrong_leaf_path: camino seguido hasta la hoja equivocada.
        wrong_leaf_id: id de la hoja equivocada (la que el jugador rechazó).
        new_animal_name: nombre normalizado del animal pensado.
        distinguishing_question: pregunta normalizada que distingue
            ``new_animal_name`` del animal de la hoja equivocada.
        new_animal_answer: respuesta que daría el nuevo animal a esa
            pregunta.

    Returns:
        Nuevo ``KnowledgeTree`` con la inserción aplicada (el original
        no se muta).
    """
    new_nodes: dict[NodeId, Node] = dict(tree.nodes)
    new_animal_id = tree.next_id
    new_question_id = NodeId(tree.next_id + 1)

    new_nodes[new_animal_id] = Animal(name=new_animal_name)
    if new_animal_answer:
        new_question = Question(
            text=distinguishing_question,
            yes=new_animal_id,
            no=wrong_leaf_id,
        )
    else:
        new_question = Question(
            text=distinguishing_question,
            yes=wrong_leaf_id,
            no=new_animal_id,
        )
    new_nodes[new_question_id] = new_question

    # Reapuntar el padre (o la raíz) a la nueva pregunta.
    new_root = tree.root
    if not wrong_leaf_path:
        new_root = new_question_id
    else:
        parent_step = wrong_leaf_path[-1]
        parent = new_nodes[parent_step.node_id]
        if not isinstance(parent, Question):  # pragma: no cover - invariante de walk
            raise CorruptedKnowledgeBaseError("padre en el camino no es una pregunta")
        if parent_step.answered_yes:
            new_nodes[parent_step.node_id] = Question(
                text=parent.text,
                yes=new_question_id,
                no=parent.no,
            )
        else:
            new_nodes[parent_step.node_id] = Question(
                text=parent.text,
                yes=parent.yes,
                no=new_question_id,
            )

    return KnowledgeTree(
        nodes=new_nodes,
        root=new_root,
        next_id=NodeId(new_question_id + 1),
    )


def list_animals(tree: KnowledgeTree) -> tuple[str, ...]:
    """Devuelve los nombres únicos de animales presentes en el árbol, ordenados."""
    names = {node.name for node in tree.nodes.values() if isinstance(node, Animal)}
    return tuple(sorted(names, key=str.casefold))
