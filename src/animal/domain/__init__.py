"""Dominio puro del juego ANIMAL.

Sin IO, sin red, sin reloj. Solo dataclasses inmutables, funciones puras
y errores. Todo lo que ocurre aquí es testeable sin mocks.
"""

from __future__ import annotations

from animal.domain.errors import (
    AnimalError,
    CorruptedKnowledgeBaseError,
    InteractionError,
    InvalidAnswerError,
    KnowledgeBaseError,
    KnowledgeBaseVersionError,
)
from animal.domain.knowledge import (
    Animal,
    Answer,
    KnowledgeTree,
    Node,
    NodeId,
    Question,
    Step,
    WalkResult,
    default_tree,
    learn,
    list_animals,
    walk,
)
from animal.domain.text import normalize_animal_name, normalize_question

__all__ = [
    "Animal",
    "AnimalError",
    "Answer",
    "CorruptedKnowledgeBaseError",
    "InteractionError",
    "InvalidAnswerError",
    "KnowledgeBaseError",
    "KnowledgeBaseVersionError",
    "KnowledgeTree",
    "Node",
    "NodeId",
    "Question",
    "Step",
    "WalkResult",
    "default_tree",
    "learn",
    "list_animals",
    "normalize_animal_name",
    "normalize_question",
    "walk",
]
