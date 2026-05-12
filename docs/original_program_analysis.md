# Análisis arqueológico de `animal.bas`

## Encuadre

| Campo | Valor |
|---|---|
| Programa | ANIMAL ("Guess the Animal") |
| Autor | Arthur Luehrmann |
| Año | 1973 (Dartmouth), publicado en 1978 |
| Lenguaje | BASIC (dialecto Microsoft BASIC / portable a MS-BASIC, Applesoft, CBM, Sinclair, Locomotive, MSX) |
| Plataforma canónica elegida | IBM PC / GW-BASIC (es el listado más fiel a la edición del libro) |
| Tamaño | 47 líneas numeradas, ~1.5 KB |
| Origen | David H. Ahl, *BASIC Computer Games*, 1978, pp. 4-5 |
| IO | `INPUT` desde teclado, `PRINT` con `TAB` a teletipo / monitor 80×24 |

### Sinopsis funcional

El programa juega a "adivina el animal". Empieza con un conocimiento
mínimo de dos animales (`FISH` y `BIRD`) y una sola pregunta que los
discrimina (`DOES IT SWIM`). En cada ronda:

1. Recorre un árbol binario de preguntas hasta llegar a una hoja
   (candidato animal).
2. Pregunta si el animal del jugador es ese candidato.
3. Si acierta, lo celebra y vuelve al menú.
4. Si falla, pide al jugador el nombre del animal pensado y una pregunta
   que lo distinga del candidato, y la incorpora al árbol.

El comando `LIST` enumera los animales conocidos en columnas de 4.

### Lectura crítica

El programa es un caso de manual de aprendizaje supervisado del usuario:
no hay aprendizaje estadístico, solo crecimiento manual del árbol.
Lo notable para su época (1973) es la representación del árbol: en BASIC
plano sin estructuras de datos, el autor codifica cada nodo en un único
string usando marcadores delimitadores (`\Q`, `\A`, `\Y`, `\N`) y un
único array `A$(200)` donde la posición 0 guarda el contador de nodos
ocupados y las demás los nodos. Es esencialmente una *arena
allocator* de strings, decisión obligada por el coste prohibitivo en
memoria de RAM cell de la época (un VAX 11/780 tenía 8 MB y la mayoría
de microcomputadoras menos de 64 KB).

## Arqueología

### Grafo de flujo

```text
           ┌─────────────────────────────────────────┐
           │ 10-110  splash + carga inicial          │
           │  DATA "4","\\QDOES IT SWIM\\Y2\\N3\\",  │
           │       "\\AFISH","\\ABIRD"               │
           └─────────────────────────────────────────┘
                            │
                            ▼
           ┌─────────────────────────────────────────┐
   ┌──────►│ 120-150  main loop                      │
   │       │  INPUT "ARE YOU THINKING OF AN ANIMAL"  │
   │       │  if "LIST" → 600                        │
   │       │  if not Y → loop                        │
   │       └─────────────────────────────────────────┘
   │                        │
   │                        ▼
   │       ┌─────────────────────────────────────────┐
   │       │ 160      K = 1   (raíz)                 │
   │       └─────────────────────────────────────────┘
   │                        │
   │              ┌─────────┘
   │              ▼
   │       ┌─────────────────────────────────────────┐
   │       │ 170      GOSUB 390  (recorre pregunta)  │
   │       └─────────────────────────────────────────┘
   │                        │
   │                        ▼
   │       ┌─────────────────────────────────────────┐
   │       │ 180-190  if leaf empty → END            │
   │       │          if node is Q  → 170 (recurre)  │
   │       └─────────────────────────────────────────┘
   │                        │ (es hoja \A)
   │                        ▼
   │       ┌─────────────────────────────────────────┐
   │       │ 200-230  "IS IT A ..." Y → vuelve a 120 │
   │       └─────────────────────────────────────────┘
   │                        │ N
   │                        ▼
   │       ┌─────────────────────────────────────────┐
   │       │ 240-380  aprende nuevo animal           │
   │       │   inserta 2 nodos en Z1 y Z1+1          │
   │       │   reescribe nodo K como pregunta nueva  │
   │       └──────────────────┬──────────────────────┘
   │                          │
   └──────────────────────────┘
                              
           ┌─────────────────────────────────────────┐
           │ 390-520  SUBRUTINA recorrer pregunta    │
           │   imprime el texto entre \Q y \         │
           │   INPUT C$ (Y/N)                        │
           │   busca \Y o \N → siguiente índice K    │
           └─────────────────────────────────────────┘

           ┌─────────────────────────────────────────┐
           │ 600-680  LIST de animales conocidos     │
           │   recorre A$(1..200) buscando \A...     │
           │   imprime en 4 columnas, vuelve a 120   │
           └─────────────────────────────────────────┘
```

### Inventario de variables

| Variable | Línea | Propósito |
|---|---|---|
| `A$(200)` | 70 | Arena de strings; cada slot un nodo |
| `A$(0)` | 110, 330-340 | Contador de slots ocupados (almacenado como string) |
| `N` | 110 | Contador inicial (= 4); en la práctica no se usa después |
| `K` | 160, 510 | Índice del nodo actual en el recorrido |
| `A$` | 130, 210, 290 | Buffer de input multipropósito (mala práctica) |
| `Q$` | 400 | Texto del nodo actual durante el recorrido |
| `C$` | 420 | Respuesta Y/N del jugador durante el recorrido |
| `T$` | 450 | Marcador a buscar (`\Y` o `\N`) |
| `X`, `Y`, `Z` | 410-500, 624 | Índices de bucle |
| `V$` | 240 | Nombre del nuevo animal aprendido |
| `X$` | 270 | Texto de la pregunta diferenciadora |
| `B$` | 310-320 | Respuesta opuesta (para construir el otro brazo) |
| `Z1` | 330-370 | Siguiente slot libre en la arena |

### Inventario de subrutinas

- **GOSUB 390** (líneas 390-520): "recorrer una pregunta". Lee el texto
  entre `\Q` y el primer `\` siguiente, pide Y/N, encuentra el marcador
  `\Y` o `\N`, y lee el índice que le sigue hasta el próximo `\`. Deja
  `K` apuntando al hijo.

### Codificación de nodos (clave del programa)

Un slot es un string. Los hay de dos tipos:

- **Animal (hoja)**: `\AGATO` significa "soy el animal GATO".
- **Pregunta (interno)**: `\QDOES IT SWIM\Y2\N3\` significa
  "pregunto DOES IT SWIM; si sí, ir al slot 2; si no, ir al slot 3".

El estado inicial es:

| slot | contenido |
|---|---|
| 0 | `"4"` (próximo libre) |
| 1 | `"\QDOES IT SWIM\Y2\N3\"` |
| 2 | `"\AFISH"` |
| 3 | `"\ABIRD"` |

Cuando aprende un animal nuevo, el algoritmo:

1. Copia el contenido del nodo equivocado `K` al slot `Z1` (lo
   archiva).
2. Mete el nuevo animal en `Z1+1`.
3. Reescribe `K` como pregunta nueva apuntando a `Z1+1` (respuesta del
   nuevo animal) y a `Z1` (respuesta opuesta, donde está el antiguo).
4. Incrementa `A$(0)` en 2.

Es un esquema de inserción in-place sobre el nodo padre, sin
re-balanceo. El árbol degenera fácilmente si el jugador insiste en
distinguir cada animal del último.

### Algoritmos identificados

1. **Búsqueda en árbol binario** con representación serializada.
2. **Inserción de hoja con división de nodo** (split-on-fail).
3. **Parseo de strings con marcadores delimitadores**, esencialmente
   un mini-DSL embebido en strings.

### Bugs y rarezas

| Linea | Síntoma | Notas |
|---|---|---|
| 110 | `N = VAL(A$(0))` se carga pero nunca se lee; sustituido por `Z1 = VAL(A$(0))` en 330 | Restos de iteración previa. |
| 180 | `IF LEN(A$(K))=0 THEN 999` salta a `END` si encuentra slot vacío. Solo ocurriría con un árbol corrupto. Pretende protección defensiva pero termina el programa sin diagnóstico. | Lo cubrimos como excepción de dominio en el port. |
| 230 | Si el jugador dice Y a "IS IT A ...", el programa imprime `WHY NOT TRY ANOTHER ANIMAL?`. Es una respuesta encantadora pero ligeramente prepotente (asume que el jugador estaba intentando engañar). | Se conserva el espíritu, suavizado. |
| 415, 640 | El `NEXT Z` dentro de la sentencia `IF ... THEN PRINT ...: NEXT Z` es ambigüedad clásica de MS-BASIC: en algunos dialectos el `NEXT` se ejecuta solo en la rama THEN, en otros siempre. Funciona porque cuando la condición es falsa (encontramos `\`) salimos del bucle con `Z` apuntando al `\`, y la siguiente sentencia es `INPUT C$` que sigue al bucle. | Comportamiento dependiente de implementación. Lo corregimos. |
| 200 | `PRINT "IS IT A ";` no añade signo de interrogación. Estilo de la época: el `INPUT` posterior lo añade implícitamente con `?`. | Conservado en TUI con tipografía moderna. |
| 270 | El programa pide la pregunta diferenciadora pero no fuerza terminación con `?`. Si el jugador escribe sin signo, los recorridos posteriores se ven raros. | Lo normalizamos en el port. |
| 300 | Bucle de validación Y/N en 280-300. Si el jugador no responde Y ni N, vuelve a preguntar la respuesta inicial sin reimprimir el contexto. Confuso. | Mejorado en el port. |
| 475, 505 | `STOP` dejaba al jugador en el prompt de BASIC sin diagnóstico. | Convertido a excepciones tipadas. |
| Todo el programa | Las preguntas se almacenan en MAYÚSCULAS y sin normalización. Si el jugador escribe `does it fly?` la pregunta queda en minúsculas. | El port normaliza con sentence case y añade signo. |

### IO y dispositivos

- Solo `INPUT` y `PRINT`. Sin sprites, sin sonido, sin POKE a memoria de
  pantalla. Es de los pocos programas del libro Ahl totalmente
  agnósticos de plataforma: corre igual en cualquier BASIC con
  manipulación de strings.

### Persistencia

Ninguna. Al salir del intérprete BASIC se pierde el árbol completo.
**El port añade persistencia JSON** como mejora 2026 (ver
`docs/adr/0004-persistence.md`).

## Bugs corregidos (en el port)

1. Validación de Y/N robusta con reimpresión de contexto (línea 300
   original).
2. Normalización de preguntas a sentence case y signo `?` final.
3. Mensajes de error tipados en lugar de `STOP` mudo.
4. Detección de slot vacío convertida en `CorruptedKnowledgeBaseError`.
5. El comportamiento del bucle `NEXT Z` con `IF...THEN` (línea 415, 640)
   se sustituye por un walker explícito sin ambigüedad.
