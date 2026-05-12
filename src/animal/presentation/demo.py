"""Guion determinista para ``animal --demo``.

Reproduce una sesión completa sin intervención humana:
1. Acierta con "pez".
2. Falla con "ave" y enseña "murciélago".
3. Lista los animales.
4. Sale.

El guion no depende del RNG (la mecánica del juego es determinista),
pero el ``--seed`` se aplica al ``StdRng`` por consistencia con la CLI.
"""

from __future__ import annotations

DEMO_SCRIPT: tuple[str, ...] = (
    "sí",  # ¿Estás pensando en un animal?
    "sí",  # ¿Nada?
    "sí",  # ¿Es un pez? -> acierto
    "sí",  # ¿Estás pensando en un animal?
    "no",  # ¿Nada?
    "no",  # ¿Es un ave? -> fallo
    "murciélago",  # ¿En qué animal pensabas?
    "tiene plumas",  # pregunta diferenciadora
    "no",  # ¿Para un murciélago, la respuesta sería?
    "list",  # listar
    "salir",
)
