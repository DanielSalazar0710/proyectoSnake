# Avance del proyecto

**Versión:** 0.1 (bosquejo inicial)
**Archivo principal:** [`src/snake.mas`](src/snake.mas)

## Qué funciona

| Funcionalidad | Estado | Cómo se comprueba |
| --- | --- | --- |
| Limpiar el tablero (256 celdas en negro) | ✅ | Al ejecutar, el display queda negro |
| Dibujar la cabeza (verde) y el punto (rojo) | ✅ | Cabeza en (8, 4), punto en (8, 10) |
| Mostrar el puntaje inicial `0` con `OUTPUT` | ✅ | Primera salida = 0 |
| Leer la dirección con `INPUT` | ✅ | |
| Rechazar entradas inválidas (distintas de 1–4) | ✅ | Escribir 7 o 0: no se mueve y vuelve a pedir |
| Mover arriba, abajo, izquierda y derecha | ✅ | La celda anterior vuelve a negro y la nueva se pinta de verde |
| Choque con pared → fin de partida | ✅ | Imprime `9999` y el puntaje final, luego `Halt` |
| Comer el punto → puntaje + 1 | ✅ | Imprime el nuevo puntaje |
| Prueba de colores del display | ✅ | [`pruebas/prueba_colores.mas`](pruebas/prueba_colores.mas) |

Por ahora la serpiente es **solo la cabeza** (una celda). Toda la estructura de entrada, validación, movimiento, dibujo y fin de partida ya está separada en secciones y subrutinas, para agregar el cuerpo sobre ella.

## Pruebas realizadas

Las pruebas se corrieron en **MARIE.js** y también con el simulador del repositorio (`scripts/simulador_marie.py`), que da los mismos resultados.

| Prueba | Entradas | Salidas (`OUTPUT`) | Resultado |
| --- | --- | --- | --- |
| Inicio | — | `0` | Cabeza en (8, 4), punto en (8, 10) |
| Inválidas y 4 direcciones | `7 0 1 3 2 4` | `0` | 7 y 0 se ignoran; la cabeza da la vuelta y vuelve a (8, 4) |
| Comer el punto | `4 4 4 4 4 4` | `0 1` | La cabeza llega a (8, 10) y el puntaje sube a 1 |
| Pared derecha | `4` × 12 | `0 1 9999 1` | Come en el camino, llega a la columna 15 y choca |
| Pared izquierda | `7 3 3 3 3 3` | `0 9999 0` | Llega a la columna 0 y choca. Probado también en MARIE.js |

Resultado del display después de comer el punto (simulador, `S` = serpiente):

```
. . . . . . . . . . . . . . . .
...
. . . . . . . . . . S . . . . .   <- fila 8, columna 10
...
```

Las entradas de cada prueba están en [`pruebas/entradas/`](pruebas/entradas/).

## Decisiones tomadas

- **Posición de la celda:** guardamos `Fila` y `Col` por separado porque así revisar las paredes es solo comparar con 0 y con 15. La dirección en el display se calcula con `F00 + 16·Fila + Col` en la subrutina `CalcularDireccion`. Como MARIE no tiene multiplicación, se suma 16 tantas veces como indique `Fila`.
- **Colores:** el display de MARIE.js usa RGB 5‑5‑5, por eso verde es `0x03E0` y rojo `0x7C00`.
- **Fin de partida:** se imprime `9999` para marcar que terminó y luego el puntaje final.
- **Subrutinas:** se llaman con `JnS` y regresan con `JumpI`, una subrutina por tarea (dibujar, borrar, calcular dirección, limpiar).

## Pendiente

1. **Cuerpo con buffer circular** (`Cuerpo`, `IdxCabeza`, `IdxCola`, `Largo`) y movimiento de la cola.
2. **Crecer** una celda al comer (la cola no avanza en ese turno).
3. **Nuevo punto** desde una tabla fija de posiciones, saltando las celdas ocupadas.
4. **Choque con el propio cuerpo**, considerando que la celda que libera la cola es válida.
5. **Rechazo del giro de 180°** cuando la serpiente tiene más de una celda (ya se guarda `Direccion` para esto).
6. **Tablero completo** cuando no queda celda libre.
7. Capturas de MARIE.js para cada prueba, short paper y póster.
