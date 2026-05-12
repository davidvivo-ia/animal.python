"""Modo headless: REPL puro (sin Textual).

Útil para entornos donde no hay terminal interactivo decente: SSH con
pipes, CI, grabación de transcripts, scripts de demo. Comparte motor
con la TUI (``GameSession``).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from animal.application import GameSession
from animal.domain import Animal, Question
from animal.domain.errors import InvalidAnswerError
from animal.domain.text import parse_yes_no


def _print_banner(console: Console) -> None:
    title = Text("ANIMAL", style="bold #F2B233")
    subtitle = Text(
        "creative computing — morristown, new jersey",
        style="#8B7355",
    )
    console.print(Panel.fit(Text.assemble(title, "\n", subtitle), border_style="#574236"))
    console.print(
        "[#E8D4B8]Piensa en un animal y yo intentaré adivinarlo.[/]\n"
        "[#8B7355]Comandos: 'list' anima los conocidos, 'salir' sale.[/]\n"
    )


def _print_animals(console: Console, animals: tuple[str, ...]) -> None:
    if not animals:
        console.print("[#8B7355]Aún no conozco ningún animal.[/]\n")
        return
    console.print(f"\n[#F2B233]Conozco {len(animals)} animal(es):[/]")
    width = max(len(a) for a in animals) + 2
    cols = 4
    line = ""
    for idx, name in enumerate(animals, start=1):
        line += f"{name:<{width}}"
        if idx % cols == 0:
            console.print(line)
            line = ""
    if line:
        console.print(line)
    console.print()


def run_repl(
    session: GameSession,
    *,
    console: Console | None = None,
    inputs: Iterable[str] | None = None,
) -> int:
    """Ejecuta el REPL.

    Args:
        session: sesión de juego ya abierta.
        console: consola Rich; si ``None`` se crea una nueva.
        inputs: iterable de líneas pre-grabadas (modo demo); si ``None``,
            se lee de stdin.

    Returns:
        Código de salida (0 en éxito).
    """
    console = console or Console()
    _print_banner(console)

    iterator = _line_iterator(inputs)
    rounds = 0
    while True:
        line = _next_line(iterator, prompt="¿Estás pensando en un animal? ", console=console)
        if line is None:
            break
        cmd = line.strip().lower()
        if cmd in {"", "salir", "quit", "exit", "q"}:
            break
        if cmd in {"list", "ls", "lista"}:
            _print_animals(console, session.known_animals())
            continue
        try:
            yes = parse_yes_no(cmd)
        except InvalidAnswerError:
            console.print("[#E07A5F]Responde sí/no, o 'list'/'salir'.[/]")
            continue
        if not yes:
            console.print("[#8B7355]Vale, vuelve cuando quieras.[/]")
            continue
        if not _play_round(session, console, iterator):
            break
        rounds += 1

    _print_animals(console, session.known_animals())
    console.print(
        f"[#7FB069]Hasta luego. Aciertos: {session.stats.correct_guesses} / "
        f"{session.stats.rounds_played}. Aprendí "
        f"{session.stats.animals_learned}.[/]",
    )
    return 0


def _play_round(
    session: GameSession,
    console: Console,
    iterator: Iterator[str | None],
) -> bool:
    """Devuelve ``False`` si el usuario aborta la sesión (EOF / 'salir')."""
    node = session.start_round()
    while isinstance(node, Question):
        ans = _ask_yes_no(node.text, iterator, console)
        if ans is None:
            return False
        node = session.answer(yes=ans)
    assert isinstance(node, Animal)
    confirm = _ask_yes_no(f"¿Es un {node.name}?", iterator, console)
    if confirm is None:
        return False
    if confirm:
        console.print("[#7FB069]¡Bien! Intenta con otro animal cuando quieras.[/]\n")
        session.confirm_correct()
        return True

    name = _ask_text(
        "Me rindo. ¿En qué animal pensabas?",
        iterator,
        console,
    )
    if name is None:
        return False
    question = _ask_text(
        f"Dame una pregunta de sí/no que distinga un {name} de un {node.name}.",
        iterator,
        console,
    )
    if question is None:
        return False
    new_ans = _ask_yes_no(f"Para un {name}, la respuesta sería", iterator, console)
    if new_ans is None:
        return False
    session.teach_new_animal(
        new_animal_raw=name,
        distinguishing_question_raw=question,
        new_animal_answers_yes=new_ans,
    )
    console.print(f"[#7FB069]Apuntado: ya conozco al {name}.[/]\n")
    return True


def _ask_yes_no(prompt: str, iterator: Iterator[str | None], console: Console) -> bool | None:
    while True:
        line = _next_line(iterator, prompt=f"{prompt} ", console=console)
        if line is None:
            return None
        try:
            return parse_yes_no(line)
        except InvalidAnswerError:
            console.print("[#E07A5F]Por favor, responde sí o no.[/]")


def _ask_text(prompt: str, iterator: Iterator[str | None], console: Console) -> str | None:
    while True:
        line = _next_line(iterator, prompt=f"{prompt} ", console=console)
        if line is None:
            return None
        if line.strip():
            return line
        console.print("[#E07A5F]Respuesta vacía, escribe algo.[/]")


def _line_iterator(inputs: Iterable[str] | None) -> Iterator[str | None]:
    if inputs is None:
        return _stdin_iterator()
    return _scripted_iterator(inputs)


def _stdin_iterator() -> Iterator[str | None]:
    while True:
        try:
            yield input()
        except EOFError:
            yield None
            return


def _scripted_iterator(inputs: Iterable[str]) -> Iterator[str | None]:
    yield from inputs
    yield None


def _next_line(iterator: Iterator[str | None], *, prompt: str, console: Console) -> str | None:
    console.print(prompt, end="", style="#F2B233")
    line = next(iterator, None)
    if line is None:
        console.print()
        return None
    console.print(line, style="#E8D4B8")
    return line
