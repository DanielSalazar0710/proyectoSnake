#!/usr/bin/env python3
"""
Simulador sencillo de MARIE para probar los programas .mas sin abrir el navegador.

Uso:
    python3 scripts/simulador_marie.py src/snake.mas D D D D D D
    python3 scripts/simulador_marie.py src/snake.mas --archivo pruebas/entradas/02_comer_punto.txt

Cada entrada puede ser un numero (como el Input en modo DECIMAL) o una
sola letra (como el Input en modo UNICODE: se usa su codigo ASCII, W = 87).

Ensambla el programa (dos pasadas, como MARIE.js), lo ejecuta con las entradas
dadas y muestra las salidas (OUTPUT) y el display 16x16 en texto:
    .  fondo      S  serpiente      o  comida      #  otro color

Este script es solo una herramienta de apoyo para probar: toda la logica
del juego esta en el programa MARIE.
"""
import sys

OPCODES = {
    "jns": 0x0, "load": 0x1, "store": 0x2, "add": 0x3, "subt": 0x4,
    "input": 0x5, "output": 0x6, "halt": 0x7, "skipcond": 0x8, "jump": 0x9,
    "clear": 0xA, "addi": 0xB, "jumpi": 0xC, "loadi": 0xD, "storei": 0xE,
}
SIN_OPERANDO = {"input", "output", "halt", "clear"}

FONDO, SERPIENTE, COMIDA = 0x0000, 0x03E0, 0x7C00


def limpiar(linea):
    return linea.split("/", 1)[0].strip()


def ensamblar(texto):
    lineas = []
    for num, cruda in enumerate(texto.splitlines(), 1):
        l = limpiar(cruda)
        if not l:
            continue
        etiqueta = None
        if "," in l:
            etiqueta, l = l.split(",", 1)
            etiqueta, l = etiqueta.strip(), l.strip()
        partes = l.split()
        lineas.append((num, etiqueta, partes))

    simbolos = {}
    for dir_, (num, et, _) in enumerate(lineas):
        if et:
            if et in simbolos:
                raise SystemExit(f"Linea {num}: etiqueta repetida {et}")
            simbolos[et] = dir_

    mem = [0] * 4096
    for dir_, (num, et, partes) in enumerate(lineas):
        op = partes[0].lower()
        arg = partes[1] if len(partes) > 1 else None
        if op == "dec":
            mem[dir_] = int(arg) & 0xFFFF
        elif op == "hex":
            mem[dir_] = int(arg, 16) & 0xFFFF
        elif op in OPCODES:
            if op in SIN_OPERANDO:
                operando = 0
            elif op == "skipcond":
                operando = int(arg, 16)
            else:
                if arg not in simbolos:
                    raise SystemExit(f"Linea {num}: etiqueta desconocida {arg}")
                operando = simbolos[arg]
            mem[dir_] = (OPCODES[op] << 12) | operando
        else:
            raise SystemExit(f"Linea {num}: instruccion desconocida {partes[0]}")
    if len(lineas) > 0xF00:
        raise SystemExit("El programa invade la memoria del display (F00)")
    return mem, len(lineas)


def con_signo(v):
    return v - 0x10000 if v & 0x8000 else v


def valor_entrada(texto):
    # una letra sola se toma como en el modo UNICODE de MARIE.js (codigo ASCII)
    if len(texto) == 1 and not texto.isdigit():
        return ord(texto)
    return int(texto)


def ejecutar(mem, entradas, max_pasos=2_000_000):
    ac, pc, salidas = 0, 0, []
    entradas = list(entradas)
    for _ in range(max_pasos):
        ir = mem[pc]
        op, x = ir >> 12, ir & 0xFFF
        pc = (pc + 1) & 0xFFF
        if op == 0x0:   mem[x] = pc; pc = (x + 1) & 0xFFF
        elif op == 0x1: ac = mem[x]
        elif op == 0x2: mem[x] = ac
        elif op == 0x3: ac = (ac + mem[x]) & 0xFFFF
        elif op == 0x4: ac = (ac - mem[x]) & 0xFFFF
        elif op == 0x5:
            if not entradas:
                return salidas, "esperando INPUT (se acabaron las entradas)"
            ac = valor_entrada(entradas.pop(0)) & 0xFFFF
        elif op == 0x6: salidas.append(con_signo(ac))
        elif op == 0x7: return salidas, "HALT"
        elif op == 0x8:
            c = (x >> 10) & 0x3
            v = con_signo(ac)
            if (c == 0 and v < 0) or (c == 1 and v == 0) or (c == 2 and v > 0):
                pc = (pc + 1) & 0xFFF
        elif op == 0x9: pc = x
        elif op == 0xA: ac = 0
        elif op == 0xB: ac = (ac + mem[mem[x] & 0xFFF]) & 0xFFFF
        elif op == 0xC: pc = mem[x] & 0xFFF
        elif op == 0xD: ac = mem[mem[x] & 0xFFF]
        elif op == 0xE: mem[mem[x] & 0xFFF] = ac
        else: raise SystemExit(f"Opcode invalido {op:X} en {pc-1:03X}")
    return salidas, "demasiados pasos (bucle infinito?)"


def display(mem):
    simb = {FONDO: ".", SERPIENTE: "S", COMIDA: "o"}
    filas = []
    for f in range(16):
        filas.append(" ".join(simb.get(mem[0xF00 + 16 * f + c], "#") for c in range(16)))
    return "\n".join(filas)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ruta, resto = sys.argv[1], sys.argv[2:]
    if resto[:1] == ["--archivo"]:
        with open(resto[1]) as f:
            entradas = []
            for linea in f:
                entradas += linea.split("#", 1)[0].split()
    else:
        entradas = resto
    with open(ruta) as f:
        mem, n = ensamblar(f.read())
    salidas, fin = ejecutar(mem, entradas)
    print(f"Palabras ensambladas: {n} (0x000 - 0x{n-1:03X})")
    print(f"Entradas: {' '.join(entradas) or '(ninguna)'}")
    print(f"Salidas (OUTPUT): {salidas}")
    print(f"Termino por: {fin}")
    print(display(mem))


if __name__ == "__main__":
    main()
