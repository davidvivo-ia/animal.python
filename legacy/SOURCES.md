# Procedencia del código legacy

## `ibm_pc/animal.bas`

- **Programa**: ANIMAL ("Guess the Animal").
- **Autor original**: Arthur Luehrmann (Dartmouth College).
- **Publicación canónica**: David H. Ahl, *BASIC Computer Games*
  (Creative Computing Press, Morristown, New Jersey, 1978), pp. 4-5.
- **Listado descargado**: <https://raw.githubusercontent.com/GReaperEx/bcg/master/animal.bas>
  (transcripción fiel del listado de la edición Microcomputer de 1978).
- **Plataforma de referencia**: MS-BASIC / Microsoft BASIC sobre IBM PC
  (BASICA, GW-BASIC), pero el dialecto es portable a cualquier BASIC con
  `DIM`/`READ`/`DATA`/`MID$`/`LEFT$`/`RIGHT$`/`VAL`/`STR$` y `GOTO`/`GOSUB`,
  cosa que incluye Sinclair BASIC del ZX Spectrum, Applesoft, CBM BASIC,
  Locomotive y MSX BASIC con cambios menores.
- **Estatus legal**: David Ahl liberó los listados del libro como dominio
  público de facto en 1978 y reafirmó en la edición online de
  <https://www.atariarchives.org/basicgames/> y
  <https://www.vintage-basic.net/games.html>. Considerado abandonware
  educativo. Se incluye aquí como artefacto histórico inmutable.

## Lectura de la sustitución

No ha habido sustitución de género: el usuario pidió portar `animal.bas`
y eso es exactamente lo que existe en `legacy/`. La transcripción del
repositorio GReaperEx/bcg coincide línea a línea con el listado original
del libro (verificado contra la copia de vintage-basic.net), salvo por la
codificación de `\` en lugar del backslash gráfico de algunos terminales
de la época.

## Otras versiones consideradas

Existen ports históricos a Sinclair BASIC y Applesoft, pero ofrecen
exactamente la misma estructura algorítmica (mismo árbol binario
codificado en strings con marcadores `\Q`/`\A`/`\Y`/`\N`). Se omite su
inclusión para no duplicar.
