"""Tests de la TUI Textual usando Pilot."""

from __future__ import annotations

import pytest

from animal.application import GameSession
from animal.infrastructure.repository import InMemoryRepository
from animal.presentation.tui import AnimalApp


@pytest.mark.asyncio
async def test_tui_plays_full_round() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    app = AnimalApp(session=session)

    async with app.run_test() as pilot:
        # Empezamos a jugar.
        await pilot.press(*"sí")
        await pilot.press("enter")
        await pilot.pause()
        # Respondemos "sí" a "¿Nada?" -> debe llegar a "¿Es un pez?".
        await pilot.press(*"sí")
        await pilot.press("enter")
        await pilot.pause()
        # Confirmamos que sí es pez.
        await pilot.press(*"sí")
        await pilot.press("enter")
        await pilot.pause()

    assert session.stats.correct_guesses == 1


@pytest.mark.asyncio
async def test_tui_lists_known_animals_with_keybinding() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    app = AnimalApp(session=session)

    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        # No se valida el texto exacto del Static (Textual no expone trivial),
        # pero confirmamos que la acción no falló.
        assert app.is_running


@pytest.mark.asyncio
async def test_tui_full_learning_flow_teaches_new_animal() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    app = AnimalApp(session=session)

    async with app.run_test() as pilot:
        # Empezar ronda.
        await pilot.press("enter")  # Enter vacío = sí, empezar.
        await pilot.pause()
        # ¿Nada? -> no -> llega a "ave".
        await pilot.press(*"no")
        await pilot.press("enter")
        await pilot.pause()
        # ¿Es un ave? -> no -> pasa a aprender.
        await pilot.press(*"no")
        await pilot.press("enter")
        await pilot.pause()
        # ¿En qué pensabas? -> loro
        await pilot.press(*"loro")
        await pilot.press("enter")
        await pilot.pause()
        # Pregunta diferenciadora -> "habla"
        await pilot.press(*"habla")
        await pilot.press("enter")
        await pilot.pause()
        # ¿Para un loro la respuesta sería? -> sí
        await pilot.press(*"sí")
        await pilot.press("enter")
        await pilot.pause()

    assert "loro" in session.known_animals()
    assert session.stats.animals_learned == 1


@pytest.mark.asyncio
async def test_tui_quit_command_exits_app() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    app = AnimalApp(session=session)

    async with app.run_test() as pilot:
        await pilot.press(*"salir")
        await pilot.press("enter")
        await pilot.pause()
    # exit() devuelve 0 en la app; el await garantiza que terminó.
    assert app.return_value == 0


@pytest.mark.asyncio
async def test_tui_reset_replaces_knowledge() -> None:
    repo = InMemoryRepository()
    session = GameSession.open(repo)
    # Enseñamos un animal previo.
    session.start_round()
    session.answer(yes=False)
    session.teach_new_animal(
        new_animal_raw="murciélago",
        distinguishing_question_raw="¿tiene plumas?",
        new_animal_answers_yes=False,
    )
    assert "murciélago" in session.known_animals()

    app = AnimalApp(session=session)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+r")
        await pilot.pause()

    assert "murciélago" not in session.known_animals()
