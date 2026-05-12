# Arquitectura

## Diagrama de capas

```text
   ┌──────────────────────────────────────────────────────────┐
   │                     presentation/                        │
   │   ┌────────────────┐    ┌────────────────────────────┐   │
   │   │  cli.py (Typer)│───►│  tui.py (Textual app)      │   │
   │   │  --seed --demo │    │  screens, widgets, CSS     │   │
   │   └───────┬────────┘    └──────────────┬─────────────┘   │
   └───────────┼────────────────────────────┼─────────────────┘
               │                            │
               ▼                            ▼
   ┌──────────────────────────────────────────────────────────┐
   │                     application/                         │
   │     GameSession  ◄─── orquesta dominio + infra           │
   │     casos: walk, learn, list, save, load                 │
   └──────────────┬──────────────────────────┬────────────────┘
                  │                          │
                  ▼                          ▼
   ┌──────────────────────────┐   ┌─────────────────────────┐
   │       domain/            │   │    infrastructure/      │
   │  KnowledgeTree (frozen)  │   │  JsonRepository         │
   │  Node, NodeId, Answer    │   │  Rng (Protocol + impl)  │
   │  pure functions:         │   │  Paths (XDG)            │
   │  walk(), learn(),        │   │                         │
   │  list_animals()          │   │                         │
   │  exceptions              │   │                         │
   └──────────────────────────┘   └─────────────────────────┘

   ▲ las flechas son dependencias permitidas: solo hacia abajo.
   ▲ domain no importa de application/infrastructure/presentation.
   ▲ application importa solo de domain y de Protocols definidos en domain.
   ▲ infrastructure implementa Protocols de domain.
```

## Reglas de dependencia

1. `domain/` es puro: ni IO, ni red, ni reloj, ni RNG global, ni
   pydantic, ni Textual. Solo `dataclasses`, `typing` y errores propios.
2. `application/` orquesta dominio. Recibe colaboradores por
   parámetros (inyección por argumento). Puede importar
   `domain.protocols`.
3. `infrastructure/` implementa los protocolos del dominio (`Rng`,
   `KnowledgeRepository`). Aquí vive pydantic v2 para la fronteras IO.
4. `presentation/` conoce `application/` y `infrastructure/` para
   ensamblar el contenedor. Es el único módulo que toca Textual,
   Typer y stdout.

## Modelo de dominio

- `NodeId = NewType("NodeId", int)`.
- `Animal`, `Question` → variantes de `Node` con `frozen=True,
  slots=True`.
- `KnowledgeTree` es un `dataclass(frozen=True)` que envuelve un
  `Mapping[NodeId, Node]` inmutable. Toda mutación devuelve un nuevo
  árbol (estilo persistente, copy-on-write).
- `walk(tree, answers) -> WalkResult`: devuelve la hoja alcanzada y el
  camino tomado.
- `learn(tree, path, new_animal, question, new_answer) -> KnowledgeTree`:
  reescritura inmutable del árbol con nuevo nodo pregunta y nueva hoja.

## Persistencia

- Formato canónico: JSON anidado con `kind: "question"|"animal"`.
- Localización por defecto: `$XDG_DATA_HOME/animal/knowledge.json` o
  `~/.local/share/animal/knowledge.json`.
- Validación de entrada con pydantic v2 (`KnowledgeFileV1` model). El
  modelo se convierte a/desde el dominio en `infrastructure/repository.py`.
- Versionado: la raíz del fichero lleva `"version": 1`. Migración
  futura prevista en `migrations/`.

## Concurrencia / atomicidad

Una sola sesión, sin concurrencia. Persistencia con escritura
`write-then-rename` para evitar truncados ante Ctrl-C.

## Errores

Jerarquía:

```text
AnimalError                  (raíz, mensaje en es)
├── KnowledgeBaseError
│   ├── CorruptedKnowledgeBaseError
│   └── KnowledgeBaseVersionError
└── InteractionError
    └── InvalidAnswerError
```

Los errores son del dominio. La presentación los traduce a UI.
