"""Normalización de texto del dominio.

Mantiene aquí (puro, testeable) las reglas que en el BASIC original
quedaban implícitas y dependían del dialecto.
"""

from __future__ import annotations

import unicodedata

from animal.domain.errors import InvalidAnswerError

_YES_WORDS: frozenset[str] = frozenset(
    {"y", "yes", "s", "si", "sí", "1", "true", "t", "verdadero", "v"}
)
_NO_WORDS: frozenset[str] = frozenset({"n", "no", "0", "false", "f", "falso"})


def parse_yes_no(raw: str) -> bool:
    """Parsea una respuesta sí/no en es/en y devuelve ``bool``.

    Args:
        raw: cadena tal como la introdujo el jugador.

    Returns:
        ``True`` si la respuesta es afirmativa, ``False`` si negativa.

    Raises:
        InvalidAnswerError: si la cadena no es reconocible.
    """
    cleaned = _strip_accents(raw.strip().lower())
    if cleaned in _YES_WORDS:
        return True
    if cleaned in _NO_WORDS:
        return False
    raise InvalidAnswerError(raw)


def normalize_animal_name(raw: str) -> str:
    """Normaliza el nombre de un animal: minúsculas + recorte de espacios."""
    cleaned = " ".join(raw.split()).lower()
    if not cleaned:
        raise InvalidAnswerError(raw)
    return cleaned


def normalize_question(raw: str) -> str:
    """Normaliza una pregunta diferenciadora.

    - Recorta espacios.
    - Pone en mayúscula la primera letra.
    - Garantiza signo de interrogación final (``?``).
    """
    cleaned = " ".join(raw.split())
    if not cleaned:
        raise InvalidAnswerError(raw)
    cleaned = cleaned.strip("?¿").strip()
    if not cleaned:
        raise InvalidAnswerError(raw)
    cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned + "?"


def _strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )
