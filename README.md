# Snake en MARIE

Proyecto de la materia **Organización de Computadores**.
Implementación del juego Snake (el clásico de Nokia) en lenguaje ensamblador de **MARIE**, ejecutándose en **[MARIE.js](https://marie.js.org/)** y usando su display gráfico de 16 × 16.

> Este documento es la **propuesta** del grupo: cómo pensamos resolver el problema.
> El estado actual del trabajo está en [AVANCE.md](AVANCE.md) y la explicación del código en [EXPLICACION_CODIGO.md](EXPLICACION_CODIGO.md).

**Integrantes:** _(por completar)_

---

## 1. Objetivo

Construir una versión jugable de Snake **por turnos**: en cada turno el jugador escribe una dirección con `INPUT`, la serpiente avanza una celda y el display se actualiza. La serpiente come puntos, crece una celda y suma 1 al puntaje por cada punto. La partida termina si la cabeza choca contra una pared o contra su propio cuerpo, o si el tablero se llena.

## 2. Convenciones del juego

### 2.1 Direcciones (entrada con `INPUT`, modo decimal)

| Entrada | Dirección | Cambio en la posición |
| --- | --- | --- |
| 1 | Arriba | fila − 1 |
| 2 | Abajo | fila + 1 |
| 3 | Izquierda | columna − 1 |
| 4 | Derecha | columna + 1 |

Cualquier otro número se rechaza y se vuelve a pedir **sin mover** la serpiente. Cuando la serpiente tenga más de una celda, también se rechazará el giro de 180° (por ejemplo, pedir izquierda cuando se va a la derecha).

### 2.2 Colores

El display de MARIE.js lee la memoria `0xF00`–`0xFFF` y cada palabra es un color **RGB 5‑5‑5** (bits 14‑10 rojo, 9‑5 verde, 4‑0 azul).

| Elemento | Color | Valor |
| --- | --- | --- |
| Fondo | Negro | `0x0000` |
| Serpiente | Verde | `0x03E0` |
| Punto (comida) | Rojo | `0x7C00` |

### 2.3 Tablero

- 16 filas × 16 columnas. La fila 0 es la de arriba y la columna 0 la de la izquierda.
- La celda `(fila, columna)` está en la dirección de memoria **`F00 + 16·fila + columna`**.
- Posición inicial: cabeza en **fila 8, columna 4**, mirando a la **derecha** (dirección 4).
- Primer punto: **fila 8, columna 10** (`0xF8A`).

### 2.4 Salidas con `OUTPUT`

- Al inicio se imprime el puntaje (`0`).
- Cada vez que la serpiente come se imprime el nuevo puntaje.
- Al terminar la partida se imprime el **código de fin `9999`** y después el **puntaje final**.
  (Para el caso de tablero completo se usará otro código, por definir.)

## 3. Representación en memoria (propuesta)

### 3.1 Cuerpo de la serpiente: buffer circular

El cuerpo se guarda como una **cola circular** de 256 palabras (una por cada celda posible del tablero). Cada palabra guarda la **dirección de memoria del display** de un segmento (`F00`–`FFF`).

```
Cuerpo:  [ s0 | s1 | s2 | ... | s255 ]
               ^cola           ^cabeza
```

- `IdxCabeza`: índice del segmento de la cabeza.
- `IdxCola`: índice del último segmento (la cola).
- `Largo`: número de segmentos.

Al **moverse sin comer**: se agrega la nueva cabeza (`IdxCabeza + 1`), se pinta, se borra la celda de la cola y se avanza `IdxCola + 1`. El largo no cambia.
Al **comer**: se agrega la nueva cabeza pero **la cola no avanza**, así que el largo aumenta en 1.
Cuando un índice llega a 256 vuelve a 0 (por eso es circular). Así no hay que desplazar todo el cuerpo en cada turno.

### 3.2 Otras variables

| Variable | Qué guarda |
| --- | --- |
| `Fila`, `Col` | Fila y columna de la cabeza (0–15). Se usan para detectar paredes. |
| `Direccion` | Dirección actual (1–4). Se usa para rechazar el giro de 180°. |
| `ComidaDir` | Dirección de memoria del punto actual. |
| `TablaComida` | Secuencia fija de posiciones para los puntos. Si la siguiente está ocupada, se busca la siguiente celda libre. |
| `Puntaje` | Puntos obtenidos. |
| `Estado` | 0 = jugando, 1 = chocó con pared, 2 = chocó con su cuerpo, 3 = tablero completo. |

### 3.3 Detección de colisiones

- **Pared:** antes de mover se revisa si `Fila` o `Col` ya están en 0 o 15 en la dirección pedida. Si es así, la partida termina (no aparece al otro lado).
- **Cuerpo:** el display mismo sirve como mapa: si la celda a la que entra la cabeza ya tiene el color de la serpiente, es choque. Para que entrar en la celda que la cola acaba de liberar sea válido, primero se borra la cola (cuando no se come) y después se revisa la celda nueva.
- **Tablero completo:** si `Largo` llega a 256 no queda celda libre para el punto.

## 4. Estructura del programa

El programa se organiza en secciones y subrutinas cortas (`JnS` / `JumpI`):

1. **Inicio:** limpiar tablero, dibujar serpiente y punto, mostrar puntaje 0.
2. **Turno:** leer dirección y validarla (1–4, sin giro de 180°).
3. **Movimiento:** calcular la nueva cabeza, revisar pared.
4. **Comer / cola:** si hay punto, crecer y sumar puntaje; si no, mover la cola.
5. **Choque con el cuerpo.**
6. **Nuevo punto** en una celda libre.
7. **Fin de partida:** imprimir `9999` y el puntaje, `Halt`.

## 5. Estructura del repositorio

```
src/snake.mas                  programa principal (lo que se carga en MARIE.js)
pruebas/prueba_colores.mas     prueba del display y de los colores
pruebas/entradas/*.txt         entradas para cada prueba
scripts/simulador_marie.py     simulador de MARIE en Python para repetir las pruebas
README.md                      esta propuesta
AVANCE.md                      estado actual del trabajo
EXPLICACION_CODIGO.md          explicación del código
```

## 6. Cómo ejecutar

1. Abrir <https://marie.js.org/> y pegar el contenido de `src/snake.mas`.
2. Abrir el panel **Display** y poner el **Input** y el **Output** en modo **Decimal**.
3. Presionar **Assemble** y luego **Run**.
4. En cada turno escribir 1, 2, 3 o 4.

Para repetir las pruebas sin abrir el navegador:

```
python3 scripts/simulador_marie.py src/snake.mas --archivo pruebas/entradas/02_comer_punto.txt
```

El simulador solo ejecuta el programa MARIE y dibuja el display en texto; no contiene lógica del juego.

## 7. Plan de trabajo

| Etapa | Contenido | Estado |
| --- | --- | --- |
| 1 | Variables, colores, dibujo del tablero, movimiento de la cabeza en 4 direcciones, paredes, puntaje | Hecho (bosquejo) |
| 2 | Cuerpo con buffer circular, movimiento de la cola | Pendiente |
| 3 | Crecimiento al comer, nuevo punto en celda libre (tabla fija) | Pendiente |
| 4 | Choque con el cuerpo, giro de 180°, tablero completo | Pendiente |
| 5 | Pruebas mínimas con capturas del display | Pendiente |
| 6 | Short paper IEEE (Overleaf) y póster | Pendiente |

## 8. Pruebas que se van a demostrar

1. Movimiento en las cuatro direcciones y rechazo de entradas inválidas.
2. Movimiento sin comer manteniendo la longitud.
3. Comer un punto: crece una celda, puntaje + 1, nuevo punto en celda libre.
4. Choque con una pared y fin con puntaje final.
5. Choque con el propio cuerpo y fin con puntaje final.
6. Rechazo del giro de 180° con más de una celda.
7. Entrar en la celda que la cola acaba de liberar (sin crecer) es válido.
