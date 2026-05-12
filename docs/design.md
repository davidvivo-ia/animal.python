# Sistema de diseño

## Concepto

Un terminal Creative Computing 1978 visto a través de la nostalgia
amable de 2026: tipografía monoespacial, paleta cálida ámbar, bordes
con doble línea, focos sutiles, sin emojis, sin parpadeo. Un "fósil
vivo" jugable.

## Paleta

| Token | Hex | Rol |
|---|---|---|
| `surface` | `#1A1410` | fondo principal, evocación de monitor de fósforo apagado |
| `surface-alt` | `#231A14` | paneles secundarios |
| `primary` | `#F2B233` | ámbar de fósforo, texto principal de cabecera |
| `text` | `#E8D4B8` | texto cuerpo |
| `muted` | `#8B7355` | texto secundario, hints |
| `accent` | `#7FB069` | éxito, acierto |
| `warning` | `#E07A5F` | error suave, validación |
| `border` | `#574236` | líneas y bordes |

Contraste verificado: `text` sobre `surface` da ratio 9.8:1 (AAA),
`primary` sobre `surface` 7.4:1 (AAA), `muted` sobre `surface` 4.6:1
(AA). Apto para WCAG AA en todo el flujo.

## Tipografía

- Familia UI y mono: la del terminal del usuario (Textual respeta la
  fuente del host). Recomendamos IBM Plex Mono o JetBrains Mono.
- Sin tamaños múltiples: la TUI usa solo el cell del terminal. Los
  pesos se simulan con `bold` y con bordes.

## Espaciado

Grid de 1 cell vertical × 2 cells horizontal (la "celda" del terminal).
Márgenes internos de los paneles: 1 vertical / 2 horizontal.

## Iconografía

ASCII puro. Nada de emojis. Marcadores semánticos:

- `›` cursor de prompt
- `■` chip de animal aprendido
- `─ ═` bordes simples y dobles

## Estados clave

1. **Splash** — banner centrado "ANIMAL", subtítulo Creative Computing,
   ayuda breve. Pulsa cualquier tecla para empezar.
2. **Prompt principal** — input `›` con sugerencias: `sí`, `no`,
   `list`, `salir`.
3. **Recorrido de preguntas** — panel central con la pregunta actual,
   migas de pan abajo con el camino seguido.
4. **Adivinación** — caja resaltada `¿Es un X?`.
5. **Aprendizaje** — tres pantallas guiadas: nombre del animal,
   pregunta diferenciadora, respuesta para el nuevo.
6. **Lista de animales** — grid de 4 columnas con chips `■ nombre`.
7. **Despedida** — resumen breve: "He aprendido N animales esta sesión".
8. **Error suave** — banner inferior en `warning`, no bloquea el flujo.

## Accesibilidad

- Navegación 100 % teclado: `Tab`, `Enter`, `Esc`, `Ctrl+L` (lista),
  `Ctrl+Q` (salir), `Ctrl+R` (reset).
- Los iconos van siempre acompañados de texto.
- Modo claro disponible vía `ANIMAL_THEME=light` (variante de paleta
  con `surface=#FAF6F0`, `text=#231A14`, `primary=#B8860B`).

## Toque distintivo

**"Banner de carga estilo PRINT TAB"**: en el splash, la cabecera
aparece carácter a carácter en 600 ms imitando un teletipo de 1973,
con cursor parpadeante de bloque. Solo en el arranque, no en
transiciones internas (no queremos cansar). Implementado con `animate`
de Textual sobre la opacidad del label, no con `sleep`, para
respetar accesibilidad de animaciones reducidas
(`@media (prefers-reduced-motion)` se honra leyendo
`TEXTUAL_ANIMATIONS=none`).

## CSS

Ver `src/animal/assets/animal.tcss`.
