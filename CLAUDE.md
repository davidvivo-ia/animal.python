# CLAUDE.md

## Misión

Tomar un programa de los años 80 (BASIC ZX Spectrum, Amstrad CPC, Sega
Mega Drive/Genesis, Commodore 64, MSX, Apple II, IBM PC, etc.) y
reconstruirlo como obra de software de 2026: juego completo, jugable,
empaquetado, testeado, documentado y con diseño visual cuidado.

Preservas la lógica funcional y el "alma" del original. Reimaginas todo
lo demás.

No es traducción línea a línea. Es reinterpretación con criterio de
ingeniero senior y sensibilidad de diseñador.

---

Resumen operativo (la versión completa de la especificación quedó en la
conversación de arranque del proyecto). Reglas clave que aplican a
cualquier sesión de desarrollo sobre este repo:

- Python 3.13+, `uv`, `src/` layout, capas `domain` / `application` /
  `infrastructure` / `presentation`.
- Dominio puro con `dataclass(frozen=True, slots=True)`; `pydantic` v2
  en fronteras IO.
- TUI con `textual` (CSS en `src/animal/assets/`) y CLI con `typer`.
- Calidad innegociable: `ruff check`, `ruff format --check`,
  `mypy --strict src`, `pytest` con cobertura ≥80 % en `domain/`.
- `legacy/` es read-only; archivo histórico.
- RNG inyectado, modo `--seed`, modo `--demo` determinista.
- Mensajes al jugador en español; código, logs y commits en inglés;
  documentación en español.
- Trabajas autónomamente: decides, documentas en ADRs, sigues.
