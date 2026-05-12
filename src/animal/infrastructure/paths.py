"""Rutas estándar (XDG) para almacenamiento de usuario."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "animal"
APP_AUTHOR = "animal.python"


def default_db_path() -> Path:
    """Devuelve la ruta por defecto a la base de conocimiento."""
    directory = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "knowledge.json"
