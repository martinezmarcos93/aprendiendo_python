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
