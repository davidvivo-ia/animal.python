# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y versionado [SemVer](https://semver.org/lang/es/).

## [1.0.0] — 2026-05-12

Primera versión jugable y completa. Reconstrucción de `animal.bas`
(Arthur Luehrmann, Creative Computing 1973) como obra de software 2026.

### Preservado del original

- Mecánica de árbol binario de preguntas Y/N.
- Estado inicial con `fish` y `bird` y la pregunta `¿Nada?`.
- Comando `list` para ver los animales conocidos.
- Flujo "adivina → corrige → aprende pregunta diferenciadora".
- Mensaje guiño "¿por qué no intentas con otro animal?" cuando acierto.

### Modernizado

- Árbol persistente inmutable (copy-on-write) en lugar del array plano
  de strings con marcadores `\Q\Y\N\A`.
- Modelo de dominio puro con `frozen=True, slots=True`.
- Capa de aplicación con casos de uso explícitos.
- Capa de presentación TUI con Textual + CLI Typer.
- Estética fósforo ámbar (paleta WCAG AA).

### Añadido

- Persistencia JSON v1 en `$XDG_DATA_HOME/animal/knowledge.json`,
  con escritura atómica.
- Modo `--demo` determinista (sin TUI) para CI y grabación de GIFs.
- Modo `--headless` para sesiones por SSH o pipes.
- Modo `--seed N` para RNG reproducible.
- Modo `--reset` para volver al árbol inicial.
- Validación robusta de Y/N en español e inglés.
- Normalización de preguntas a sentence case con signo final.
- Atajos de teclado documentados.
- Suite de tests unitarios, de integración y de propiedad
  (`hypothesis`).
- CI con matriz Python 3.13 / 3.14.

### Licencias creativas tomadas

- [LICENCIA CREATIVA] El BASIC original no persiste nada. Añadimos
  persistencia JSON. Justificación: en 2026 esperamos memoria entre
  sesiones; sin ella el juego pierde su única forma de progresar.
- [LICENCIA CREATIVA] Mensajes al usuario en español (audiencia
  hispanohablante) en lugar del inglés original.
- [LICENCIA CREATIVA] El árbol inicial usa la pregunta `¿Nada?` en
  lugar de `DOES IT SWIM`. Significado idéntico.
- [LICENCIA CREATIVA] Splash con efecto teletipo amortiguado, no en
  el original.

### Bugs corregidos respecto al original

- Línea 300 original: validación Y/N que pierde el contexto al fallar.
  Resuelto con re-prompt explícito.
- Línea 270 original: pregunta diferenciadora sin normalización de
  signo `?`. Resuelto.
- Línea 475/505 original: `STOP` mudo en árboles corruptos. Resuelto
  con `CorruptedKnowledgeBaseError` que se traduce a UI.
- Línea 415/640 original: ambigüedad `IF...THEN PRINT...: NEXT Z` con
  dependencia de implementación. Sustituido por walker explícito.
- Línea 180 original: `LEN(A$(K))=0 → END` sin diagnóstico. Resuelto.
