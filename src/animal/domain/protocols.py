"""Protocols del dominio (puertos).

El dominio declara qué necesita; la infraestructura lo implementa.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from animal.domain.knowledge import KnowledgeTree


@runtime_checkable
class Rng(Protocol):
    """Fuente de aleatoriedad inyectable."""

    def random(self) -> float:
        """Devuelve un float en [0.0, 1.0)."""

    def choice(self, seq: list[str]) -> str:
        """Devuelve un elemento aleatorio de la secuencia (no vacía)."""


class KnowledgeRepository(Protocol):
    """Persistencia del árbol de conocimiento."""

    def load(self) -> KnowledgeTree:
        """Carga el árbol; devuelve el por defecto si no hay nada guardado."""

    def save(self, tree: KnowledgeTree) -> None:
        """Persiste el árbol de forma atómica."""
