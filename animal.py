"""ANIMAL — guess-the-animal learning game.

Modern Python port of the 1973 Creative Computing BASIC original
(https://github.com/GReaperEx/bcg/blob/master/animal.bas).

The original encoded its decision tree as backslash-delimited strings inside a
flat array. We use a real binary tree, persist it as JSON between runs, and
expose a small CLI.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB = Path.home() / ".animal_kb.json"
COLUMNS = 4


@dataclass
class Node:
    kind: str  # "animal" | "question"
    value: str
    yes: "Node | None" = None
    no: "Node | None" = None

    @classmethod
    def animal(cls, name: str) -> "Node":
        return cls(kind="animal", value=name)

    @classmethod
    def question(cls, text: str, yes: "Node", no: "Node") -> "Node":
        return cls(kind="question", value=text, yes=yes, no=no)

    def to_dict(self) -> dict:
        if self.kind == "animal":
            return {"kind": "animal", "value": self.value}
        assert self.yes is not None and self.no is not None
        return {
            "kind": "question",
            "value": self.value,
            "yes": self.yes.to_dict(),
            "no": self.no.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        if data["kind"] == "animal":
            return cls.animal(data["value"])
        return cls.question(
            data["value"],
            cls.from_dict(data["yes"]),
            cls.from_dict(data["no"]),
        )


def default_tree() -> Node:
    return Node.question(
        "Does it swim?",
        yes=Node.animal("fish"),
        no=Node.animal("bird"),
    )


def load_tree(path: Path) -> Node:
    if not path.exists():
        return default_tree()
    try:
        return Node.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"warning: could not read {path} ({exc}); starting fresh.", file=sys.stderr)
        return default_tree()


def save_tree(tree: Node, path: Path) -> None:
    path.write_text(
        json.dumps(tree.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def ask_yes_no(prompt: str) -> bool:
    yes_words = {"y", "yes", "s", "si", "sí", "1", "true", "t"}
    no_words = {"n", "no", "0", "false", "f"}
    while True:
        answer = input(f"{prompt} ").strip().lower()
        if answer in yes_words:
            return True
        if answer in no_words:
            return False
        print("  please answer yes or no.")


def ask_text(prompt: str) -> str:
    while True:
        text = input(f"{prompt} ").strip()
        if text:
            return text
        print("  empty answer, try again.")


def collect_animals(node: Node) -> list[str]:
    if node.kind == "animal":
        return [node.value]
    assert node.yes is not None and node.no is not None
    return collect_animals(node.yes) + collect_animals(node.no)


def list_animals(tree: Node) -> None:
    animals = sorted(set(collect_animals(tree)), key=str.lower)
    print(f"\nI already know {len(animals)} animal(s):")
    width = max(len(a) for a in animals) + 2
    for i, name in enumerate(animals, start=1):
        end = "\n" if i % COLUMNS == 0 else ""
        print(f"{name:<{width}}", end=end)
    if len(animals) % COLUMNS:
        print()
    print()


def play_round(tree: Node) -> Node:
    """Walk the tree with the player; teach a new animal on a wrong guess."""
    node = tree
    path: list[tuple[Node, bool]] = []
    while node.kind == "question":
        went_yes = ask_yes_no(node.value)
        path.append((node, went_yes))
        nxt = node.yes if went_yes else node.no
        assert nxt is not None
        node = nxt

    if ask_yes_no(f"Is it a {node.value}?"):
        print("Great — I guessed it!\n")
        return tree

    new_animal = ask_text("I give up. What animal were you thinking of?").lower()
    print(
        f"Give me a yes/no question that tells a "
        f"{new_animal} apart from a {node.value}."
    )
    question = ask_text(">").rstrip("?") + "?"
    new_is_yes = ask_yes_no(f"For a {new_animal}, the answer would be?")

    replacement = (
        Node.question(question, yes=Node.animal(new_animal), no=node)
        if new_is_yes
        else Node.question(question, yes=node, no=Node.animal(new_animal))
    )

    if not path:
        return replacement

    parent, branch = path[-1]
    if branch:
        parent.yes = replacement
    else:
        parent.no = replacement
    print(f"Got it — I've learned about the {new_animal}.\n")
    return tree


def banner() -> None:
    width = 60
    print("=" * width)
    print("ANIMAL".center(width))
    print("creative computing — morristown, new jersey".center(width))
    print("=" * width)
    print("Think of an animal and I'll try to guess it.")
    print("Commands: 'list' shows what I know, 'quit' exits.\n")


def main_loop(tree: Node, db_path: Path) -> Node:
    banner()
    while True:
        try:
            cmd = input("Are you thinking of an animal? ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return tree

        match cmd:
            case "" | "quit" | "exit" | "q":
                return tree
            case "list" | "ls":
                list_animals(tree)
            case _ if cmd[:1] in {"y", "s"}:
                tree = play_round(tree)
                save_tree(tree, db_path)
            case _:
                print("(say 'yes' to play, 'list' to see animals, 'quit' to leave)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guess-the-animal learning game (modern Python port of the 1973 BASIC).",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"path to the JSON knowledge base (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="discard saved knowledge and start from the built-in defaults",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tree = default_tree() if args.reset else load_tree(args.db)
    try:
        tree = main_loop(tree, args.db)
    finally:
        save_tree(tree, args.db)
    print("Bye!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
