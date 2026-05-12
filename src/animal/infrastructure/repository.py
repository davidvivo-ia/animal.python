"""Persistencia JSON v1 con validación pydantic.

Una implementación adicional ``InMemoryRepository`` se usa en tests para
no tocar disco.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from animal.domain.errors import (
    CorruptedKnowledgeBaseError,
    KnowledgeBaseError,
    KnowledgeBaseVersionError,
)
from animal.domain.knowledge import (
    Animal,
    KnowledgeTree,
    Node,
    NodeId,
    Question,
    default_tree,
)

SCHEMA_VERSION = 1


class _AnimalDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["animal"]
    name: str = Field(min_length=1)


class _QuestionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["question"]
    text: str = Field(min_length=1)
    yes: _AnimalDTO | _QuestionDTO
    no: _AnimalDTO | _QuestionDTO


class _KnowledgeFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int
    root: _AnimalDTO | _QuestionDTO


_QuestionDTO.model_rebuild()


def _node_to_dto(tree: KnowledgeTree, node_id: NodeId) -> _AnimalDTO | _QuestionDTO:
    node = tree.node(node_id)
    if isinstance(node, Animal):
        return _AnimalDTO(kind="animal", name=node.name)
    return _QuestionDTO(
        kind="question",
        text=node.text,
        yes=_node_to_dto(tree, node.yes),
        no=_node_to_dto(tree, node.no),
    )


def _tree_to_file(tree: KnowledgeTree) -> _KnowledgeFile:
    return _KnowledgeFile(version=SCHEMA_VERSION, root=_node_to_dto(tree, tree.root))


def _dto_to_nodes(
    dto: _AnimalDTO | _QuestionDTO,
    nodes: dict[NodeId, Node],
    next_id: list[int],
) -> NodeId:
    new_id = NodeId(next_id[0])
    next_id[0] += 1
    if isinstance(dto, _AnimalDTO):
        nodes[new_id] = Animal(name=dto.name)
        return new_id
    yes_id = _dto_to_nodes(dto.yes, nodes, next_id)
    no_id = _dto_to_nodes(dto.no, nodes, next_id)
    nodes[new_id] = Question(text=dto.text, yes=yes_id, no=no_id)
    return new_id


def _file_to_tree(file: _KnowledgeFile) -> KnowledgeTree:
    if file.version != SCHEMA_VERSION:
        raise KnowledgeBaseVersionError(found=file.version, expected=SCHEMA_VERSION)
    nodes: dict[NodeId, Node] = {}
    next_id = [1]
    root_id = _dto_to_nodes(file.root, nodes, next_id)
    return KnowledgeTree(nodes=nodes, root=root_id, next_id=NodeId(next_id[0]))


@dataclass(slots=True)
class JsonRepository:
    """Persistencia en un archivo JSON, escritura atómica."""

    path: Path

    def load(self) -> KnowledgeTree:
        if not self.path.exists():
            return default_tree()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CorruptedKnowledgeBaseError(f"JSON inválido: {exc}") from exc
        try:
            file = _KnowledgeFile.model_validate(raw)
        except Exception as exc:
            raise CorruptedKnowledgeBaseError(str(exc)) from exc
        return _file_to_tree(file)

    def save(self, tree: KnowledgeTree) -> None:
        file = _tree_to_file(tree)
        payload = file.model_dump_json(indent=2)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.path.parent,
            delete=False,
            prefix=".animal-",
            suffix=".tmp",
        ) as tmp:
            tmp.write(payload)
            tmp_path = Path(tmp.name)
        try:
            tmp_path.replace(self.path)
        except OSError as exc:  # pragma: no cover - filesystem dependiente
            tmp_path.unlink(missing_ok=True)
            raise KnowledgeBaseError(f"No se pudo escribir {self.path}: {exc}") from exc


@dataclass(slots=True)
class InMemoryRepository:
    """Repositorio en memoria para tests."""

    tree: KnowledgeTree = field(default_factory=default_tree)
    save_calls: int = 0

    def load(self) -> KnowledgeTree:
        return self.tree

    def save(self, tree: KnowledgeTree) -> None:
        self.tree = tree
        self.save_calls += 1
