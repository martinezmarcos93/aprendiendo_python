"""
La tortuga como REGISTRO de órdenes (sin dibujar).

El servidor no dibuja: el código del chico llama a avanzar(), girar_der(), etc. y cada
llamada se anota como una orden con el número de línea que la pidió. El navegador
recibe la lista y la anima en un <canvas> (resaltando la línea en el depurador).

Orden: {"o": "avanzar", "v": 100, "l": 3}
  o = avanzar | retroceder | girar_der | girar_izq | color | bajar_lapiz | subir_lapiz
  v = distancia, grados o color (según la orden; no existe en subir/bajar_lapiz)
  l = línea del código del chico que la pidió
"""
import math
import re

MAX_ORDENES = 5000
MAX_VALOR = 10000            # tope de distancia (evita dibujos infinitos)

# Colores en español → CSS. Los nombres en inglés y los #RRGGBB pasan tal cual.
COLORES = {
    "rojo": "red", "azul": "blue", "verde": "green", "amarillo": "gold",
    "negro": "black", "blanco": "white", "naranja": "orange", "violeta": "purple",
    "morado": "purple", "rosa": "hotpink", "celeste": "deepskyblue", "gris": "gray",
    "marron": "saddlebrown", "marrón": "saddlebrown", "turquesa": "turquoise",
    "dorado": "gold",
}
_HEX = re.compile(r"^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$")
_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ]{2,20}$")
COMANDOS = ("avanzar", "retroceder", "girar_der", "girar_izq", "color", "bajar_lapiz", "subir_lapiz")


COLOR_INICIAL = "#16a34a"
UMBRAL_DIBUJO = 0.97              # parecido mínimo para dar por igual un dibujo


class ErrorTortuga(Exception):
    """Algo que el chico le pidió mal a la tortuga (se explica en lenguaje simple)."""


def normalizar_color(valor):
    if not isinstance(valor, str):
        raise ErrorTortuga("El color tiene que ir entre comillas, por ejemplo:  color \"rojo\"")
    texto = valor.strip()
    if _HEX.match(texto):
        return texto.lower()
    if _NOMBRE.match(texto):
        return COLORES.get(texto.lower(), texto.lower())
    raise ErrorTortuga(f"No conozco el color «{texto[:20]}». Probá con \"rojo\", \"azul\", \"verde\" o un código como \"#ff8800\".")


class Registro:
    """Anota las órdenes de la tortuga. `linea` la actualiza el depurador (callback)."""

    def __init__(self, max_ordenes=MAX_ORDENES):
        self.ordenes = []
        self.linea = 0
        self.max_ordenes = max_ordenes

    def _anotar(self, orden, valor=None):
        if len(self.ordenes) >= self.max_ordenes:
            raise ErrorTortuga("Tu tortuga recibió demasiadas órdenes y la frené. ¿Hay un repetir enorme?")
        registro = {"o": orden, "l": self.linea}
        if valor is not None:
            registro["v"] = valor
        self.ordenes.append(registro)

    @staticmethod
    def _numero(nombre, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
            raise ErrorTortuga(f"{nombre} necesita un número, por ejemplo:  {nombre} 100")
        if abs(valor) > MAX_VALOR:
            raise ErrorTortuga(f"{nombre} {valor}: ese número es demasiado grande (el máximo es {MAX_VALOR}).")
        return valor

    def globales(self):
        """Funciones que se inyectan en el programa del chico."""
        def avanzar(distancia):
            self._anotar("avanzar", self._numero("avanzar", distancia))

        def retroceder(distancia):
            self._anotar("retroceder", self._numero("retroceder", distancia))

        def girar_der(grados):
            self._anotar("girar_der", self._numero("girar_der", grados))

        def girar_izq(grados):
            self._anotar("girar_izq", self._numero("girar_izq", grados))

        def color(nombre):
            self._anotar("color", normalizar_color(nombre))

        def bajar_lapiz():
            self._anotar("bajar_lapiz")

        def subir_lapiz():
            self._anotar("subir_lapiz")

        return {f.__name__: f for f in (avanzar, retroceder, girar_der, girar_izq,
                                        color, bajar_lapiz, subir_lapiz)}

    def callback_linea(self, numero):
        self.linea = numero


# ─────────────────────────────────────────
# GEOMETRÍA: qué dibujó de verdad (para comparar dibujos)
# ─────────────────────────────────────────
def trazos(ordenes):
    """Segmentos visibles (x1, y1, x2, y2, color) que dejan las órdenes. 0° = arriba, giro derecho = horario;
    misma geometría que el canvas del navegador (web/static/js/tortuga.js)."""
    x = y = rumbo = 0.0
    lapiz, color, salida = True, COLOR_INICIAL, []
    for orden in ordenes:
        nombre = orden["o"]
        if nombre in ("avanzar", "retroceder"):
            distancia = orden["v"] if nombre == "avanzar" else -orden["v"]
            radianes = math.radians(rumbo)
            nx, ny = x + math.sin(radianes) * distancia, y - math.cos(radianes) * distancia
            if lapiz and distancia != 0:
                salida.append((x, y, nx, ny, color))
            x, y = nx, ny
        elif nombre == "girar_der":
            rumbo = (rumbo + orden["v"]) % 360
        elif nombre == "girar_izq":
            rumbo = (rumbo - orden["v"]) % 360
        elif nombre == "color":
            color = orden["v"]
        elif nombre == "bajar_lapiz":
            lapiz = True
        elif nombre == "subir_lapiz":
            lapiz = False
    return salida


def _celdas(segmentos, celda=3.0):
    """El dibujo como un conjunto de celdas de 3x3 con su color: no depende del orden, del sentido
    en que se trazó ni de cuántos avanzar se usaron."""
    puestas = set()
    for x1, y1, x2, y2, color in segmentos:
        pasos = max(1, int(math.hypot(x2 - x1, y2 - y1) / 1.5))
        for k in range(pasos + 1):
            t = k / pasos
            puestas.add((round((x1 + (x2 - x1) * t) / celda), round((y1 + (y2 - y1) * t) / celda), color))
    return puestas


def similitud(ordenes_a, ordenes_b):
    """Parecido entre dos dibujos: 1.0 idénticos, 0.0 sin nada en común."""
    a, b = _celdas(trazos(ordenes_a)), _celdas(trazos(ordenes_b))
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mismo_dibujo(ordenes_a, ordenes_b):
    return bool(trazos(ordenes_a)) and similitud(ordenes_a, ordenes_b) >= UMBRAL_DIBUJO


# ─────────────────────────────────────────
# LABERINTOS: la tortuga tiene que llegar a la salida sin tocar paredes
# ─────────────────────────────────────────
# Un laberinto es un dato de la lección: {"paredes": [[x1, y1, x2, y2], ...], "salida": [x, y]}, en las mismas
# coordenadas que el dibujo (la tortuga sale de 0,0 mirando hacia arriba). No hay un camino "oficial": vale
# cualquier recorrido que no toque paredes y termine en la salida.
MARGEN_PARED = 6.0                # más cerca que esto de una pared = chocó (la tortuga tiene cuerpo)
RADIO_SALIDA = 20.0               # terminar a esta distancia de la salida = llegó
LLEGO, CHOCO, NO_LLEGO = "llego", "choco", "no_llego"


def movimientos(ordenes):
    """Cada desplazamiento de la tortuga, con el lápiz arriba o abajo: (índice de la orden, x1, y1, x2, y2).
    Misma geometría que trazos()."""
    x = y = rumbo = 0.0
    salida = []
    for i, orden in enumerate(ordenes):
        nombre = orden["o"]
        if nombre in ("avanzar", "retroceder"):
            distancia = orden["v"] if nombre == "avanzar" else -orden["v"]
            radianes = math.radians(rumbo)
            nx, ny = x + math.sin(radianes) * distancia, y - math.cos(radianes) * distancia
            salida.append((i, x, y, nx, ny))
            x, y = nx, ny
        elif nombre == "girar_der":
            rumbo = (rumbo + orden["v"]) % 360
        elif nombre == "girar_izq":
            rumbo = (rumbo - orden["v"]) % 360
    return salida


def _distancia_punto_segmento(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    largo2 = dx * dx + dy * dy
    t = 0.0 if largo2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / largo2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _se_cruzan(a, b):
    """True si los segmentos a y b (x1, y1, x2, y2) se cruzan de verdad (no solo se acercan)."""
    def lado(ox, oy, px, py, qx, qy):
        return (px - ox) * (qy - oy) - (py - oy) * (qx - ox)
    d1 = lado(*b[:2], *b[2:], *a[:2])
    d2 = lado(*b[:2], *b[2:], *a[2:])
    d3 = lado(*a[:2], *a[2:], *b[:2])
    d4 = lado(*a[:2], *a[2:], *b[2:])
    return d1 * d2 < 0 and d3 * d4 < 0


def _distancia_segmentos(a, b):
    if _se_cruzan(a, b):
        return 0.0
    return min(_distancia_punto_segmento(*a[:2], *b), _distancia_punto_segmento(*a[2:], *b),
               _distancia_punto_segmento(*b[:2], *a), _distancia_punto_segmento(*b[2:], *a))


def _choque(x1, y1, x2, y2, paredes):
    """Si el tramo toca alguna pared, cuánto se pudo avanzar antes de tocarla; si no, None."""
    tramo = (x1, y1, x2, y2)
    if all(_distancia_segmentos(tramo, p) >= MARGEN_PARED for p in paredes):
        return None
    largo = math.hypot(x2 - x1, y2 - y1)
    pasos = max(1, int(largo))                    # de a 1 unidad: alcanza para frenar pegada a la pared
    avanzado = 0.0
    for k in range(pasos + 1):
        t = k / pasos
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        if any(_distancia_punto_segmento(px, py, *p) < MARGEN_PARED for p in paredes):
            return avanzado
        avanzado = largo * t
    return avanzado


def recorrer_laberinto(ordenes, laberinto):
    """Sigue a la tortuga por el laberinto. Devuelve {"estado", "linea", "ordenes"}:
    - estado: LLEGO, CHOCO o NO_LLEGO;
    - linea: la línea del código que la hizo chocar (None si no chocó);
    - ordenes: las órdenes hasta el choque (la última, acortada hasta la pared) para que el
      navegador anime a la tortuga frenando contra la pared."""
    paredes = [tuple(p) for p in laberinto["paredes"]]
    for i, x1, y1, x2, y2 in movimientos(ordenes):
        avanzado = _choque(x1, y1, x2, y2, paredes)
        if avanzado is not None:
            hasta = [dict(o) for o in ordenes[:i + 1]]
            hasta[-1]["v"] = round(avanzado, 2)
            return {"estado": CHOCO, "linea": ordenes[i].get("l"), "ordenes": hasta}
    fin = movimientos(ordenes)
    x, y = (fin[-1][3], fin[-1][4]) if fin else (0.0, 0.0)
    sx, sy = laberinto["salida"]
    estado = LLEGO if math.hypot(x - sx, y - sy) <= RADIO_SALIDA else NO_LLEGO
    return {"estado": estado, "linea": None, "ordenes": list(ordenes)}


def problema_laberinto(laberinto):
    """Qué está mal en el dato del laberinto (para el validador), o None si está bien formado."""
    if not isinstance(laberinto, dict):
        return "«laberinto» tiene que ser un objeto con «paredes» y «salida»"
    paredes, salida = laberinto.get("paredes"), laberinto.get("salida")
    es_numero = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)  # noqa: E731
    if not isinstance(paredes, list) or not paredes:
        return "el laberinto no tiene paredes"
    for p in paredes:
        if not isinstance(p, list) or len(p) != 4 or not all(es_numero(v) for v in p):
            return f"pared mal escrita: {p!r} (van 4 números: x1, y1, x2, y2)"
    if not isinstance(salida, list) or len(salida) != 2 or not all(es_numero(v) for v in salida):
        return "la salida tiene que ser [x, y]"
    if any(_distancia_punto_segmento(0, 0, *p) < MARGEN_PARED for p in paredes):
        return "la tortuga empieza pegada a una pared"
    return None
