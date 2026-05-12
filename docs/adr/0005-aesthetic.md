# ADR 0005 — Estética: fósforo ámbar, fusión retro-moderno

## Contexto

CLAUDE.md sugiere fusión moderna-retro respetando la plataforma. El
listado original es del libro Ahl 1978, no atado a una plataforma
concreta (corría en IBM mainframes, microcomputadores y todo lo que
tuviera MS-BASIC). La metáfora más universal de la época es el
**monitor monocromo de fósforo ámbar** (DEC VT100 ámbar, IBM 5151
verde, Heath ámbar).

## Decisión

Paleta ámbar sobre marrón muy oscuro (no negro: el contraste neutro es
más cómodo a la vista en sesiones largas y nostalgia más amable). Sin
scanlines simuladas (Textual no las soporta limpiamente en todos los
terminales). Sin sonido (la plataforma original no tenía sonido en este
juego).

El **único** toque distintivo es el banner de carga teletipo del
splash. Si se quiere retro más agresivo, se ofrece `ANIMAL_THEME=crt`
como variante (no en v1.0; anotado en TODO).

## Consecuencias

- Diseño coherente con un solo tema en v1.0 + variante light.
- Documentado en `docs/design.md` con tokens hex.
- WCAG AA verificado.
