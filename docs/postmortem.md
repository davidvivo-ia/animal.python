# Postmortem

ANIMAL, escrito por Arthur Luehrmann en 1973, son 47 líneas de BASIC en
las que cabe íntegro un sistema experto de aprendizaje supervisado.
Cabe en una pantalla, se entiende en 5 minutos, se ejecuta en cualquier
microcomputador desde un IBM 1130 hasta un ZX Spectrum.

Lo hemos rehecho como proyecto de 2026 y son 12 archivos `.py`, 5 ADRs,
65 tests, un CSS para Textual, un repositorio JSON validado con pydantic
y un workflow de GitHub Actions. Probablemente unas 80× más bytes de
código (sin contar tests), para hacer **exactamente lo mismo**.

¿Qué hemos ganado? Tipado completo verificado por `mypy --strict`,
inmutabilidad estructural que hace literalmente imposible corromper el
árbol desde fuera del repositorio, persistencia que sobrevive a cierres
y caídas, tests de propiedad que dicen cosas no triviales ("toda hoja
es alcanzable, todo aprendizaje es monótono"), una capa de presentación
que separa qué se hace de cómo se ve y permite swap a CRT scanlines o
a un cliente web sin tocar dominio. Y un fichero CHANGELOG que dice qué
hemos cambiado y por qué, en lugar de un comentario `REM` de cinco
palabras.

¿Qué hemos perdido? Densidad expresiva. Inmediatez: el original arranca
con `RUN`, el nuestro pide instalar Python 3.13, uv, sincronizar y
ejecutar. Auditabilidad de bolsillo: una persona puede leer
`animal.bas` en una tarde de café, leer `animal/` requiere un mapa.
Y, paradójicamente, hemos perdido la cosa principal que hacía
emocionante al original: que cupiera entero en un disquete y se
sintiera como un truco de magia.

El oficio ha cambiado, sí, hacia más rigor, más seguridad, más
herramientas, menos sorpresa. Probablemente está bien que sea así
cuando construimos infraestructura crítica. Pero al portar un juego
educativo de 1973 a estructura moderna uno se pregunta si se habrá
hecho un favor a Luehrmann, o si más bien se le ha puesto traje de tres
piezas para una merienda en el jardín.

La respuesta personal es que ambas cosas conviven: el repositorio
`legacy/` queda intacto para quien quiera la merienda, y el `src/`
moderno para quien quiera el traje. Y que es legítimo elegir cuál
ponerse cada día.
