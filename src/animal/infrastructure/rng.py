"""Implementación de :class:`animal.domain.protocols.Rng`."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(slots=True)
class StdRng:
    """Adaptador alrededor de ``random.Random`` con seed opcional."""

    seed: int | None = None
    _rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq: list[str]) -> str:
        return self._rng.choice(seq)
