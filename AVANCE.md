# Avance del proyecto

**Versión:** 0.2 (controles W A S D y comida en lugar nuevo)
**Archivo principal:** [`src/snake.mas`](src/snake.mas)

## Qué funciona

| Funcionalidad | Estado | Cómo se comprueba |
| --- | --- | --- |
| Limpiar el tablero (256 celdas en negro) | ✅ | Al ejecutar, el display queda negro |
| Dibujar la cabeza (verde) y el punto (rojo) | ✅ | Cabeza en (8, 4), punto en (8, 10) |
| Mostrar el puntaje inicial `0` con `OUTPUT` | ✅ | Primera salida = 0 |
| Leer la tecla con `INPUT` (modo Unicode) | ✅ | W, A, S, D en mayúscula o minúscula |
| Rechazar teclas inválidas (distintas de W, A, S, D) | ✅ | Escribir X, 7 o q: no se mueve y vuelve a pedir |
| Mover arriba, abajo, izquierda y derecha | ✅ | La celda anterior vuelve a negro y la nueva se pinta de verde |
| Choque con pared → fin de partida | ✅ | Imprime `9999` y el puntaje final, luego `Halt` |
| Comer el punto → puntaje + 1 | ✅ | Imprime el nuevo puntaje |
| Nuevo punto en otra celda al comer | ✅ | Aparece en `F00 + Azar`; si la celda está ocupada se prueba otra |
| Prueba de colores del display | ✅ | [`pruebas/prueba_colores.mas`](pruebas/prueba_colores.mas) |

Por ahora la serpiente es **solo la cabeza** (una celda). Toda la estructura de entrada, validación, movimiento, dibujo y fin de partida ya está separada en secciones y subrutinas, para agregar el cuerpo sobre ella.

## Pruebas realizadas

Las pruebas se corrieron en **MARIE.js** y también con el simulador del repositorio (`scripts/simulador_marie.py`), que da los mismos resultados.

| Prueba | Entradas | Salidas (`OUTPUT`) | Resultado |
| --- | --- | --- | --- |
| Inicio | — | `0` | Cabeza en (8, 4), punto en (8, 10) |
| Inválidas y 4 direcciones | `X 7 q W a s D` | `0` | X, 7 y q se ignoran; la cabeza da la vuelta y vuelve a (8, 4) |
| Comer el punto | `D D D D D D` | `0 1` | La cabeza llega a (8, 10), el puntaje sube a 1 y el punto nuevo aparece en (13, 14) |
| Comer dos veces | `D`×6, `S`×5, `D`×4 | `0 1 2` | Come en (8, 10) y en (13, 14); el tercer punto aparece en (2, 11) |
| Pared derecha | `d` × 12 | `0 1 9999 1` | Come en el camino, llega a la columna 15 y choca |
| Pared izquierda | `A A A A A` | `0 9999 0` | Llega a la columna 0 y choca |
| MarieJS, modo Unicode | `XqDDdDDD` | `0 1` | Cada letra es un `INPUT`. Cabeza en `F8A` y punto nuevo en `F28` (8 teclas: `Azar = 296 − 256 = 40`), igual que el simulador |

Resultado del display después de comer el punto (simulador, `S` = serpiente, `o` = punto nuevo):

```
...
. . . . . . . . . . S . . . . .   <- fila 8, columna 10 (cabeza)
...
. . . . . . . . . . . . . . o .   <- fila 13, columna 14 (punto nuevo)
...
```

Las entradas de cada prueba están en [`pruebas/entradas/`](pruebas/entradas/).

## Decisiones tomadas

- **Posición de la celda:** guardamos `Fila` y `Col` por separado porque así revisar las paredes es solo comparar con 0 y con 15. La dirección en el display se calcula con `F00 + 16·Fila + Col` en la subrutina `CalcularDireccion`. Como MARIE no tiene multiplicación, se suma 16 tantas veces como indique `Fila`.
- **Colores:** el display de MARIE.js usa RGB 5‑5‑5, por eso verde es `0x03E0` y rojo `0x7C00`.
- **Fin de partida:** se imprime `9999` para marcar que terminó y luego el puntaje final.
- **Controles W A S D:** el Input de MARIE.js en modo Unicode entrega el código ASCII de la letra. Para aceptar minúsculas basta con restar 32 cuando el código es 97 o más, así solo se comparan cuatro valores.
- **Comida "aleatoria":** MARIE no tiene random. Elegimos un número `Azar` que suma 37 con cada tecla (y se queda entre 0 y 255). Es más corto que una tabla de posiciones y depende de cómo juega cada persona. Para no caer sobre la serpiente se mira el color de la celda en el display: si no es negra se prueba la siguiente.
- **Subrutinas:** se llaman con `JnS` y regresan con `JumpI`, una subrutina por tarea (dibujar, borrar, calcular dirección, limpiar).

## Pendiente

1. **Cuerpo con buffer circular** (`Cuerpo`, `IdxCabeza`, `IdxCola`, `Largo`) y movimiento de la cola.
2. **Crecer** una celda al comer (la cola no avanza en ese turno).
3. **Choque con el propio cuerpo**, considerando que la celda que libera la cola es válida.
4. **Rechazo del giro de 180°** cuando la serpiente tiene más de una celda (ya se guarda `Direccion` para esto).
5. **Tablero completo** cuando no queda celda libre.
6. Capturas de MARIE.js para cada prueba, short paper y póster.
