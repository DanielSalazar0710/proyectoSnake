# Explicación del código

Este documento explica `src/snake.mas` sección por sección. Las secciones del código están numeradas igual que aquí.

## Repaso rápido de MARIE

- Un solo registro de trabajo: el **AC** (acumulador). Casi todo es `Load` (traer a AC), operar (`Add`, `Subt`) y `Store` (guardar).
- `Skipcond 400` salta la siguiente instrucción si **AC = 0**; `Skipcond 800` si **AC > 0**; `Skipcond 000` si **AC < 0**.
- `StoreI X` guarda el AC en la dirección que está **dentro de** `X` (indirecto). Así se pinta una celda del display: en `X` está la dirección de la celda.
- `JnS Sub` guarda la dirección de regreso en la primera palabra de `Sub` y salta a la siguiente; `JumpI Sub` regresa.

## Idea general

```
Inicio: limpiar tablero, dibujar punto, dibujar cabeza, OUTPUT puntaje
repetir:
    leer entrada
    si no es 1..4: volver a leer
    si la cabeza está en el borde hacia esa dirección: FIN
    borrar la cabeza
    cambiar Fila o Col
    si hay punto y la cabeza está sobre él:
        puntaje = puntaje + 1, OUTPUT puntaje, ya no hay punto
    dibujar la cabeza
FIN: OUTPUT 9999, OUTPUT puntaje, Halt
```

## Sección 1. Inicio del programa

```
Inicio,  JnS  LimpiarTablero
         JnS  DibujarComida
         JnS  DibujarCabeza
         Load Puntaje
         Output
```

Prepara la pantalla llamando tres subrutinas y muestra el puntaje inicial (0). El orden importa: primero se limpia todo y después se pintan los elementos encima.

## Sección 2. Turno: leer y validar la dirección

Se lee un número con `Input` y se guarda en `Entrada`. Para saber cuál es, se le resta 1, 2, 3 y 4, cada vez partiendo de `Entrada`:

```
Turno,   Input
         Store   Entrada
         Subt    Uno          / Entrada - 1
         Skipcond 400         / si dio 0, la entrada era 1 ...
         Jump    NoEsUno      / ... y se salta este Jump
         Jump    MoverArriba  / ... para llegar aquí
```

Si no coincide con ninguna de las cuatro, el último bloque hace `Jump Turno`: se vuelve a pedir la entrada **sin haber movido nada**. Eso cumple la regla de rechazar entradas inválidas.

## Sección 3. Movimientos

Los cuatro bloques tienen la misma forma. Ejemplo de **derecha**:

```
MoverDerecha, Load  Col
              Subt  Quince       / Col - 15
              Skipcond 400       / si Col == 15 está en el borde derecho
              Jump  SiDerecha    / no está en el borde: se puede mover
              Jump  ChocoPared   / sí está: fin de la partida
SiDerecha,    Load  Cuatro
              Store Direccion    / se recuerda la dirección actual
              JnS   BorrarCabeza / la celda vieja vuelve a negro
              Load  Col
              Add   Uno          / Col = Col + 1
              Store Col
              Jump  DespuesDeMover
```

| Bloque | Borde que revisa | Cambio |
| --- | --- | --- |
| `MoverArriba` | `Fila == 0` | `Fila − 1` |
| `MoverAbajo` | `Fila == 15` | `Fila + 1` |
| `MoverIzquierda` | `Col == 0` | `Col − 1` |
| `MoverDerecha` | `Col == 15` | `Col + 1` |

La pared se revisa **antes** de mover. Así la cabeza nunca sale del tablero ni aparece del otro lado. Para revisar `== 0` basta con `Load` + `Skipcond 400`; para `== 15` primero se resta `Quince`.

`Direccion` se guarda en cada movimiento aunque por ahora no se usa: la vamos a necesitar para rechazar el giro de 180° cuando exista el cuerpo.

## Sección 4. Después de mover

1. Si `HayComida` es 0 (ya se comió el punto), no hay nada que revisar y se salta a pintar.
2. Si hay punto, se calcula la dirección de la cabeza (`CalcularDireccion` deja el resultado en `Dir`) y se compara con `ComidaDir` restando: si la resta da 0, la cabeza está sobre el punto.
3. Al comer: `Puntaje + 1`, se imprime, y `HayComida = 0`.
4. Siempre termina pintando la cabeza en su nueva celda (`PintarCabeza`) y volviendo a `Turno`.

Aquí es donde después se agregará el crecimiento y el nuevo punto (está marcado como `PENDIENTE` en el código).

## Sección 5. Fin de la partida

```
ChocoPared, Load  Uno
            Store Estado      / Estado = 1: perdió por pared
            Load  CodigoFin
            Output            / 9999 = la partida terminó
            Load  Puntaje
            Output            / puntaje final
            Halt
```

El fin del juego se identifica en la salida porque aparece `9999` seguido del puntaje final, y el programa se detiene con `Halt`. La variable `Estado` deja guardado en memoria por qué terminó.

## Sección 6. Subrutinas

### 6.1 `CalcularDireccion`

Convierte `(Fila, Col)` en la dirección del display: **`Dir = F00 + 16·Fila + Col`**.
MARIE no tiene multiplicación, así que se hace con un bucle:

```
Dir = F00
Contador = Fila
mientras Contador > 0:
    Dir = Dir + 16
    Contador = Contador - 1
Dir = Dir + Col
```

Ejemplo: fila 8, columna 10 → `F00 + 128 + 10 = F8A`, que es justo `ComidaDir`.

### 6.2 `DibujarCabeza` y 6.3 `BorrarCabeza`

Las dos llaman a `CalcularDireccion` y luego hacen `StoreI Dir`: la primera guarda `ColorSerpiente` y la segunda `ColorFondo`. Moverse es simplemente **borrar → cambiar fila/columna → dibujar**.

### 6.4 `DibujarComida`

`StoreI ComidaDir` con `ColorComida`. Como ya se tiene la dirección del punto, no hace falta calcularla.

### 6.5 `LimpiarTablero`

Recorre las 256 celdas con un puntero `Ptr` que empieza en `F00`, guarda `ColorFondo` en cada una y suma 1 al puntero. `Contador` empieza en 256 y baja hasta 0.

## Secciones 7 a 10. Datos

| Sección | Contenido |
| --- | --- |
| 7. Variables del juego | `Fila`, `Col`, `Direccion`, `Puntaje`, `Estado`, `ComidaDir`, `HayComida`, `Entrada` |
| 8. Colores | `ColorFondo = 0000` (negro), `ColorSerpiente = 03E0` (verde), `ColorComida = 7C00` (rojo) |
| 9. Auxiliares | `Dir`, `Ptr`, `Contador` |
| 10. Constantes | `Uno` … `Cuatro`, `Quince`, `Dieciseis`, `TotalCeldas = 256`, `PrimerPixel = F00`, `CodigoFin = 9999` |

Los datos van al final del programa para que nunca se ejecuten como instrucciones (el programa siempre termina en `Halt` o vuelve a `Turno` antes de llegar ahí).

## Dónde cambiar cosas

| Si se quiere… | Se cambia… |
| --- | --- |
| Otra posición inicial | `Fila` y `Col` en la sección 7 |
| Otro lugar para el punto | `ComidaDir` (calcular `F00 + 16·fila + columna` en hexadecimal) |
| Otros colores | Sección 8 (formato RGB 5‑5‑5) |
| Otras teclas de dirección | Las constantes que se restan en la sección 2 |
| Otro código de fin | `CodigoFin` en la sección 10 |
| Que dé más puntos por comida | El `Add Uno` de la sección 4 |
