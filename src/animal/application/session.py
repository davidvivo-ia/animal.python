"""Sesión de juego: orquesta dominio + repositorio.

Stateful en memoria (porque una partida tiene posición actual en el
árbol), pero el árbol subyacente sigue siendo inmutable: cada
aprendizaje sustituye la referencia.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from animal.domain import (
    Animal,
    KnowledgeTree,
    NodeId,
    Question,
    Step,
    list_animals,
    normalize_animal_name,
    normalize_question,
)
from animal.domain.errors import AnimalError, CorruptedKnowledgeBaseError
from animal.domain.knowledge import learn
from animal.domain.protocols import KnowledgeRepository


@dataclass(slots=True)
class SessionStats:
    """Métricas ligeras de la partida actual."""

    rounds_played: int = 0
    correct_guesses: int = 0
    animals_learned: int = 0


@dataclass(slots=True)
class GameSession:
    """Estado de una partida en curso."""

    repository: KnowledgeRepository
    tree: KnowledgeTree
    stats: SessionStats = field(default_factory=SessionStats)

    # Estado durante un recorrido en curso.
    _current_node: NodeId | None = None
    _path: list[Step] = field(default_factory=list)

    @classmethod
    def open(cls, repository: KnowledgeRepository) -> GameSession:
        """Crea una sesión cargando el árbol del repositorio."""
        return cls(repository=repository, tree=repository.load())

    # ----- recorrido ---------------------------------------------------

    def start_round(self) -> Question | Animal:
        """Comienza un nuevo recorrido desde la raíz."""
        self._current_node = self.tree.root
        self._path = []
        return self._current_view()

    def answer(self, *, yes: bool) -> Question | Animal:
        """Avanza por el árbol con una respuesta y devuelve el nuevo nodo."""
        if self._current_node is None:
            raise AnimalError("No hay ronda activa.")
        node = self.tree.node(self._current_node)
        if not isinstance(node, Question):
            raise AnimalError("Solo se puede responder ante una pregunta.")
        self._path.append(Step(node_id=self._current_node, answered_yes=yes))
        self._current_node = node.yes if yes else node.no
        return self._current_view()

    def current(self) -> Question | Animal:
        """Devuelve el nodo actual del recorrido."""
        if self._current_node is None:
            raise AnimalError("No hay ronda activa.")
        return self._current_view()

    def _current_view(self) -> Question | Animal:
        if self._current_node is None:  # pragma: no cover - guard
            raise AnimalError("No hay ronda activa.")
        return self.tree.node(self._current_node)

    # ----- desenlaces --------------------------------------------------

    def confirm_correct(self) -> None:
        """El candidato actual era el animal pensado: cierra la ronda."""
        self._require_leaf()
        self.stats.rounds_played += 1
        self.stats.correct_guesses += 1
        self._current_node = None
        self._path = []
        self.repository.save(self.tree)

    def teach_new_animal(
        self,
        *,
        new_animal_raw: str,
        distinguishing_question_raw: str,
        new_animal_answers_yes: bool,
    ) -> None:
        """Enseña un animal nuevo y persiste.

        Llamar solo después de que ``confirm_correct`` haya sido descartado
        (el jugador dijo "no, no es ese").
        """
        leaf_id = self._require_leaf()
        new_tree = learn(
            self.tree,
            wrong_leaf_path=tuple(self._path),
            wrong_leaf_id=leaf_id,
            new_animal_name=normalize_animal_name(new_animal_raw),
            distinguishing_question=normalize_question(distinguishing_question_raw),
            new_animal_answer=new_animal_answers_yes,
        )
        self.tree = new_tree
        self.stats.rounds_played += 1
        self.stats.animals_learned += 1
        self._current_node = None
        self._path = []
        self.repository.save(self.tree)

    def _require_leaf(self) -> NodeId:
        if self._current_node is None:
            raise AnimalError("No hay ronda activa.")
        node = self.tree.node(self._current_node)
        if not isinstance(node, Animal):
            raise CorruptedKnowledgeBaseError(
                "se esperaba una hoja en el nodo actual",
            )
        return self._current_node

    # ----- consultas ---------------------------------------------------

    def known_animals(self) -> tuple[str, ...]:
        """Lista de animales conocidos, ordenada."""
        return list_animals(self.tree)

    def reset_to_default(self) -> None:
        """Vuelve al árbol inicial (fish/bird) y lo persiste."""
        from animal.domain.knowledge import default_tree

        self.tree = default_tree()
        self._current_node = None
        self._path = []
        self.repository.save(self.tree)
