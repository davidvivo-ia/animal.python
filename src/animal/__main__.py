"""Permite `python -m animal`."""

from __future__ import annotations

from animal.presentation.cli import app


def main() -> None:
    """Entry point para ``python -m animal``."""
    app()


if __name__ == "__main__":
    main()
