# animal

> Reconstrucción de **ANIMAL** (Arthur Luehrmann, Creative Computing, 1973)
> como obra de software de 2026: Textual TUI, dominio puro inmutable,
> persistencia JSON, tests con propiedades, `--demo` determinista.

```text
                              ANIMAL
              creative computing — morristown, new jersey
              ─────────────────────────────────────────
              › Piensa en un animal y yo intentaré adivinarlo.
```

## Instalación

Requiere Python 3.13+ y [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run animal
```

## Uso

```bash
uv run animal                    # TUI Textual con persistencia en XDG
uv run animal --reset            # empieza desde la base de conocimiento por defecto
uv run animal --db ./mi_kb.json  # base de conocimiento alternativa
uv run animal --seed 7           # RNG reproducible
uv run animal --demo --seed 42   # guion determinista, sin TUI, ideal para CI/GIF
uv run animal --headless         # modo línea (sin Textual), útil sobre SSH/pipes
```

Atajos en la TUI:

| Tecla | Acción |
|---|---|
| `Enter` | confirmar |
| `Esc` | volver / cancelar |
| `Ctrl+L` | listar animales conocidos |
| `Ctrl+R` | reiniciar conocimiento |
| `Ctrl+Q` | salir guardando |

## Estructura

```text
src/animal/
├── domain/         # entidades inmutables, funciones puras, errores
├── application/    # casos de uso (GameSession)
├── infrastructure/ # JSON repo, RNG, paths XDG
├── presentation/   # Typer CLI + Textual TUI + modo demo
└── assets/         # CSS Textual
```

Detalles en [`docs/architecture.md`](docs/architecture.md),
[`docs/design.md`](docs/design.md) y los ADRs en
[`docs/adr/`](docs/adr/).

## Desarrollo

```bash
uv sync --dev
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
```

`pre-commit install` para activar los hooks.

## Origen

El listado original está en [`legacy/ibm_pc/animal.bas`](legacy/ibm_pc/animal.bas)
con procedencia documentada en [`legacy/SOURCES.md`](legacy/SOURCES.md).
La arqueología completa, incluyendo el grafo de flujo y los bugs
corregidos, en [`docs/original_program_analysis.md`](docs/original_program_analysis.md).

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
