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
