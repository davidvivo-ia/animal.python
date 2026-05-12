"""Jerarquía de errores del dominio.

Mensajes en español (audiencia final). Cada excepción transporta el
contexto necesario para diagnosticar.
"""

from __future__ import annotations


class AnimalError(Exception):
    """Raíz de todos los errores del dominio."""


class KnowledgeBaseError(AnimalError):
    """Problema con la base de conocimiento."""


class CorruptedKnowledgeBaseError(KnowledgeBaseError):
    """La base de conocimiento está estructuralmente rota."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Base de conocimiento corrupta: {detail}")
        self.detail = detail


class KnowledgeBaseVersionError(KnowledgeBaseError):
    """La versión del fichero no se entiende."""

    def __init__(self, found: int, expected: int) -> None:
        super().__init__(f"Versión no soportada: encontrada {found}, esperada {expected}.")
        self.found = found
        self.expected = expected


class InteractionError(AnimalError):
    """Problema en la interacción con el jugador."""


class InvalidAnswerError(InteractionError):
    """El jugador no respondió sí/no de forma reconocible."""

    def __init__(self, raw: str) -> None:
        super().__init__(f"Respuesta no reconocida: {raw!r}.")
        self.raw = raw
