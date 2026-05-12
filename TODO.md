# TODO — futuras versiones

## v1.1

1. **Deshacer último aprendizaje** (`Ctrl+Z`): aprovecha la
   inmutabilidad del árbol para pila de snapshots. Coste: pequeño.
2. **Modo CRT más agresivo** con scanlines via `rich.console` o
   widget custom de Textual.
3. **Detección de preguntas duplicadas**: si el jugador introduce una
   pregunta que ya existe en el camino, avisar y proponer afinar.
4. **Exportar/importar conocimiento** vía `animal export` / `animal
   import`, para compartir árboles.
5. **Multi-idioma**: i18n con `babel`; ya hay infraestructura para
   sí/no en es/en.

## Limitaciones conocidas v1.0

- No hay deshacer.
- No hay edición manual del árbol desde la TUI (sí editando el JSON).
- El splash teletipo no es interrumpible (debería con cualquier tecla).
- Sin tema CRT en v1.0 (sólo `default` y `light` documentado).
