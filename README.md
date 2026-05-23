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

### Windows

Tres formas, de menos a más permanente:

1. **Doble clic** sobre `scripts\animal.bat` desde el Explorador.
   El wrapper detecta `uv` o `py -3.13` automáticamente y deja la
   consola abierta al terminar.

2. **PowerShell**:

   ```powershell
   .\scripts\animal.ps1                  # TUI
   .\scripts\animal.ps1 --demo --seed 42 # demo
   ```

   Si te quejas de la política de ejecución, lanza una vez:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

3. **Instalación como herramienta** (deja `animal.exe` en el PATH):

   ```powershell
   uv tool install .          # o:  pip install --user .
   animal                     # ya disponible desde cualquier cmd / PowerShell
   animal --demo --seed 42
   ```

   Para un acceso directo en el menú Inicio, crea un atajo a
   `%USERPROFILE%\.local\bin\animal.exe` (uv) o
   `%APPDATA%\Python\Scripts\animal.exe` (pip --user).

### Sin `uv`, con Python puro

Si prefieres no usar `uv`, te basta con Python 3.13+ y `pip`. Tres
caminos según lo que vayas a hacer:

1. **Instalación editable, recomendado para desarrollo:**

   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate          # Windows:  .venv\Scripts\activate
   pip install -e .
   python -m animal                   # o simplemente:  animal
   python -m animal --demo --seed 42
   ```

   Para los gates de calidad añade el grupo dev: `pip install -e '.[dev]'`
   no está disponible (usamos `dependency-groups` de PEP 735), instala
   manualmente: `pip install pytest pytest-cov hypothesis ruff mypy
   pre-commit`.

2. **Instalación normal (usuario final):**

   ```bash
   pip install --user .
   animal
   python -m animal --demo --seed 42
   ```

3. **Sin instalar nada, ejecutar desde el repo:**

   ```bash
   pip install textual typer rich pydantic structlog platformdirs
   PYTHONPATH=src python -m animal               # Linux / macOS
   set "PYTHONPATH=src" && python -m animal      # Windows cmd
   $env:PYTHONPATH = "src"; python -m animal     # PowerShell
   ```

Ambas formas (`python -m animal` y `animal`) son equivalentes: la
primera usa `src/animal/__main__.py`, la segunda el entry-point
declarado en `pyproject.toml`.

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
