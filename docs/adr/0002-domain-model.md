# ADR 0002 — Modelo de dominio: árbol persistente inmutable

## Contexto

El BASIC original codifica el árbol como un array plano de strings con
marcadores `\Q\Y\N\A`. Es ingenioso para 1973 pero ilegible, lento de
modificar y propenso a corrupción. Nuestra prioridad es claridad y
testabilidad.

## Opciones consideradas

1. **Mismo array plano de strings** para fidelidad arqueológica. Rechazado
   por ilegible.
2. **Árbol mutable** con `Node` mutable. Rechazado: el spec pide
   inmutabilidad por defecto en dominio.
3. **Árbol persistente (copy-on-write)**: dataclasses `frozen=True,
   slots=True`, IDs estables por nodo, mapping inmutable. Cada
   "aprendizaje" devuelve un nuevo árbol. Elegido.

## Decisión

- `Node` es una unión sellada (`Animal | Question`), ambas
  `@dataclass(frozen=True, slots=True)`.
- `KnowledgeTree` envuelve `nodes: Mapping[NodeId, Node]` y `root: NodeId`,
  ambos inmutables.
- Operaciones (`walk`, `learn`) son funciones puras sobre el árbol que
  devuelven un nuevo árbol.

## Consecuencias

- Trivial de testear con propiedades (hypothesis): toda secuencia de
  `learn(...)` produce un árbol bien formado.
- Snapshots gratis para deshacer (no en v1.0, anotado en TODO).
- Pequeño coste de copia: irrelevante para árboles de ≤1000 nodos.
