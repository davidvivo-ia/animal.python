# ADR 0001 — Capa de presentación: Textual TUI con CLI Typer

## Contexto

El programa original (`legacy/ibm_pc/animal.bas`) es texto puro:
`INPUT`/`PRINT` sin caracteres semigráficos, sin POKE a pantalla, sin
sprites. Encaja al milímetro con la regla de CLAUDE.md: "Si el original
es texto puro con INPUT/PRINT y menús -> TUI con Textual".

## Opciones consideradas

1. **CLI plana con Rich** (`typer` + `rich.console.Console`). Pros:
   sencillo, robusto, igual al BASIC. Contras: no aprovecha 50 años de
   evolución de interfaces; el spec pide diseño visual cuidado.
2. **TUI con Textual**. Pros: layouts CSS, focos, animaciones discretas,
   componentes reutilizables. Contras: dependencia más pesada, curva de
   aprendizaje.
3. **pygame-ce**. Pros: gráfico real. Contras: el original no es
   gráfico; sería cosplay innecesario.

## Decisión

**Textual** como interfaz principal, con `typer` como CLI de entrada
(`--seed`, `--demo`, `--db`, `--reset`).

El modo `--demo` no abre la TUI: usa el mismo motor de aplicación con
un guion fijo y un seed determinista, y escribe a stdout con `rich`.
Esto permite grabar GIFs sin coreografía manual y cubre los tests E2E.

## Consecuencias

- Una dependencia más (`textual`) y una de tests (`textual.pilot`).
- El estilo se gobierna desde CSS en `assets/animal.tcss`, no
  desperdigado.
- La compatibilidad con redirección de stdout (pipes, CI) requiere usar
  el modo `--demo` o `--headless`. Documentado en README.
