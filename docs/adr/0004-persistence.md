# ADR 0004 — Persistencia: JSON v1 en XDG_DATA_HOME

## Contexto

El BASIC no persiste nada. Al salir del intérprete se pierde todo el
aprendizaje. En 2026 esperamos memoria entre sesiones.

## Opciones consideradas

1. **Sin persistencia** (fiel al original). Rechazado: la mecánica de
   aprendizaje pide guardar.
2. **SQLite**. Sobreingeniería para ≤1000 nodos.
3. **JSON nativo** con esquema versionado. Elegido.

## Decisión

- Formato:

  ```json
  {
    "version": 1,
    "root": "/" estructura recursiva /"
  }
  ```

- Validación con pydantic v2 en `infrastructure/repository.py`.
- Ubicación: `$XDG_DATA_HOME/animal/knowledge.json` o
  `~/.local/share/animal/knowledge.json` por defecto.
- Escritura atómica: `write_text` a tmp + `Path.replace`.
- CLI `--db` permite override.

## Consecuencias

- Curva de migración futura: nuevo `version: 2`, función `migrate_v1_v2`.
- El JSON es legible a mano, lo que ayuda en bugs reportados.
