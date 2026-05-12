"""TUI Textual del juego ANIMAL.

Una pantalla principal con un panel central que cambia su contenido
según el estado del autómata (saludo → pregunta → adivinanza →
aprendizaje → lista). Atajos globales: Ctrl+L, Ctrl+R, Ctrl+Q, Esc.
"""

from __future__ import annotations

from enum import Enum, auto
from importlib.resources import files
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static

from animal.application import GameSession
from animal.domain import Animal, Question
from animal.domain.errors import AnimalError, InvalidAnswerError
from animal.domain.text import (
    normalize_animal_name,
    normalize_question,
    parse_yes_no,
)


class _Stage(Enum):
    BEGIN = auto()
    ASK_QUESTION = auto()
    ASK_GUESS = auto()
    ASK_NEW_NAME = auto()
    ASK_NEW_QUESTION = auto()
    ASK_NEW_ANSWER = auto()
    LIST = auto()
    BYE = auto()


def _css_path() -> Path:
    resource = files("animal.assets").joinpath("animal.tcss")
    # importlib.resources.files devuelve un Traversable; con un paquete
    # instalado normalmente equivale a un Path real, pero pasamos a str
    # por compatibilidad con Textual.
    return Path(str(resource))


class AnimalApp(App[int]):
    """Aplicación Textual."""

    TITLE = "ANIMAL"
    SUB_TITLE = "creative computing — morristown, new jersey"
    CSS_PATH = _css_path()

    BINDINGS = [  # noqa: RUF012
        Binding("ctrl+l", "list_animals", "Animales"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("ctrl+q", "quit_save", "Salir"),
        Binding("escape", "back_to_begin", "Volver"),
    ]

    def __init__(self, session: GameSession) -> None:
        super().__init__()
        self._session = session
        self._stage: _Stage = _Stage.BEGIN
        self._pending_name: str = ""
        self._pending_question: str = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="main-panel"):
            yield Static(self._stage_text(), id="question-text")
            yield Static("", id="breadcrumbs")
            yield Static("", id="feedback")
            yield Input(placeholder="Escribe tu respuesta y pulsa Enter", id="player-input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    # ----- estado / pintado -------------------------------------------

    def _stage_text(self) -> str:
        match self._stage:
            case _Stage.BEGIN:
                return (
                    "Piensa en un animal y pulsa Enter para empezar.\n"
                    "(o escribe 'list' para ver lo que conozco)"
                )
            case _Stage.ASK_QUESTION:
                current = self._session.current()
                assert isinstance(current, Question)
                return current.text
            case _Stage.ASK_GUESS:
                current = self._session.current()
                assert isinstance(current, Animal)
                return f"¿Es un {current.name}?"
            case _Stage.ASK_NEW_NAME:
                return "Me rindo. ¿En qué animal pensabas?"
            case _Stage.ASK_NEW_QUESTION:
                current = self._session.current()
                assert isinstance(current, Animal)
                return (
                    f"Dame una pregunta de sí/no que distinga un "
                    f"{self._pending_name} de un {current.name}."
                )
            case _Stage.ASK_NEW_ANSWER:
                return f"Para un {self._pending_name}, la respuesta sería..."
            case _Stage.LIST:
                animals = self._session.known_animals()
                if not animals:
                    return "Aún no conozco ningún animal."
                width = max(len(a) for a in animals) + 2
                lines = []
                line = ""
                for idx, name in enumerate(animals, start=1):
                    line += f"{name:<{width}}"
                    if idx % 4 == 0:
                        lines.append(line)
                        line = ""
                if line:
                    lines.append(line)
                return "Animales que conozco:\n" + "\n".join(lines)
            case _Stage.BYE:
                return "Hasta luego."

    def _refresh(self, *, feedback: str = "") -> None:
        self.query_one("#question-text", Static).update(self._stage_text())
        self.query_one("#feedback", Static).update(feedback)

    # ----- handlers ----------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.value = ""
        try:
            self._handle(raw)
        except AnimalError as exc:
            self._refresh(feedback=f"[#E07A5F]{exc}[/]")

    def _handle(self, raw: str) -> None:
        # Comandos globales por texto.
        if raw.lower() in {"list", "ls", "lista"}:
            self._stage = _Stage.LIST
            self._refresh()
            return
        if raw.lower() in {"salir", "quit", "exit", "q"}:
            self.action_quit_save()
            return

        match self._stage:
            case _Stage.BEGIN:
                self._start_round_if_yes(raw)
            case _Stage.ASK_QUESTION:
                self._answer_question(raw)
            case _Stage.ASK_GUESS:
                self._resolve_guess(raw)
            case _Stage.ASK_NEW_NAME:
                self._pending_name = normalize_animal_name(raw)
                self._stage = _Stage.ASK_NEW_QUESTION
                self._refresh()
            case _Stage.ASK_NEW_QUESTION:
                self._pending_question = normalize_question(raw)
                self._stage = _Stage.ASK_NEW_ANSWER
                self._refresh()
            case _Stage.ASK_NEW_ANSWER:
                self._finish_learning(raw)
            case _Stage.LIST:
                # Cualquier tecla vuelve al inicio.
                self._stage = _Stage.BEGIN
                self._refresh()
            case _Stage.BYE:
                self.exit(0)

    def _start_round_if_yes(self, raw: str) -> None:
        try:
            yes = parse_yes_no(raw)
        except InvalidAnswerError:
            # Aceptamos Enter vacío como "sí, empieza".
            if raw == "":
                yes = True
            else:
                self._refresh(feedback="[#E07A5F]Responde sí o no.[/]")
                return
        if not yes:
            self._refresh(feedback="[#8B7355]Vale, dime cuando quieras.[/]")
            return
        node = self._session.start_round()
        self._stage = _Stage.ASK_QUESTION if isinstance(node, Question) else _Stage.ASK_GUESS
        self._refresh()
        self._update_breadcrumbs()

    def _answer_question(self, raw: str) -> None:
        yes = parse_yes_no(raw)
        node = self._session.answer(yes=yes)
        self._stage = _Stage.ASK_QUESTION if isinstance(node, Question) else _Stage.ASK_GUESS
        self._refresh()
        self._update_breadcrumbs()

    def _resolve_guess(self, raw: str) -> None:
        yes = parse_yes_no(raw)
        if yes:
            self._session.confirm_correct()
            self._stage = _Stage.BEGIN
            self._refresh(feedback="[#7FB069]¡Bien! ¿Otra ronda?[/]")
            return
        self._stage = _Stage.ASK_NEW_NAME
        self._refresh()

    def _finish_learning(self, raw: str) -> None:
        yes = parse_yes_no(raw)
        self._session.teach_new_animal(
            new_animal_raw=self._pending_name,
            distinguishing_question_raw=self._pending_question,
            new_animal_answers_yes=yes,
        )
        self._pending_name = ""
        self._pending_question = ""
        self._stage = _Stage.BEGIN
        self._refresh(feedback="[#7FB069]Apuntado. ¿Otra ronda?[/]")

    def _update_breadcrumbs(self) -> None:
        # Para no exponer estado interno, mostramos un contador simple.
        stats = self._session.stats
        self.query_one("#breadcrumbs", Static).update(
            f"Rondas: {stats.rounds_played}   "
            f"Aciertos: {stats.correct_guesses}   "
            f"Aprendidos: {stats.animals_learned}",
        )

    # ----- acciones ----------------------------------------------------

    def action_list_animals(self) -> None:
        self._stage = _Stage.LIST
        self._refresh()

    def action_reset(self) -> None:
        self._session.reset_to_default()
        self._stage = _Stage.BEGIN
        self._refresh(feedback="[#7FB069]Conocimiento reiniciado.[/]")

    def action_quit_save(self) -> None:
        self._stage = _Stage.BYE
        self._refresh()
        self.exit(0)

    def action_back_to_begin(self) -> None:
        self._stage = _Stage.BEGIN
        self._refresh()
