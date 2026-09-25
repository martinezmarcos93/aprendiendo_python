"""
Proceso hijo que ejecuta UN pedido y termina. Lo lanza tortuscript.proceso.

Lee un JSON por stdin y escribe un JSON por stdout. Así el código del chico corre
aislado del servidor web, con límites de tiempo y memoria puestos por el padre.

Pedido:
  {"op": "ejecutar", "fuente": "...", "entradas": [...]}
  {"op": "evaluar",  "fuente": "...", "entradas": [...], "solucion": "..."}
  {"op": "tortuga",  "fuente": "...", "entradas": [...]}   → agrega "ordenes"
"""
import json
import sys

from .evaluacion import evaluar
from .executor import ejecutar_codigo
from .tortuga import Registro
from .translator import TraductorTortuScript, detectar_tipo


def _python_de(fuente):
    tipo = detectar_tipo(fuente)
    python = fuente if tipo == "python" else TraductorTortuScript().traducir_codigo(fuente)
    return tipo, python


def atender(pedido):
    tipo, python = _python_de(pedido.get("fuente", ""))
    detalles = {}
    registro = Registro() if pedido.get("op") == "tortuga" else None
    salida, hay_error, mensaje = ejecutar_codigo(
        python, entradas_fijas=list(pedido.get("entradas") or []),
        detalles=detalles, completar_con_vacio=False,
        extra_globals=registro.globales() if registro else None,
        callback_linea=registro.callback_linea if registro else None)
    respuesta = {
        "tipo": tipo, "python": python,
        "salida": salida, "error": hay_error, "mensaje": mensaje,
        "salida_programa": detalles.get("salida_programa", ""),
        "entradas": detalles.get("entradas", []),
        "pregunta": detalles.get("pregunta_pendiente"),
    }
    if registro is not None:
        respuesta["ordenes"] = registro.ordenes       # aunque haya error: se dibuja lo hecho
    if pedido.get("op") == "evaluar" and not hay_error and respuesta["pregunta"] is None:
        respuesta["evaluacion"] = evaluar(pedido.get("solucion", ""), detalles)
    return respuesta


def main():
    for flujo in (sys.stdin, sys.stdout):   # Windows abre los pipes en cp1252
        flujo.reconfigure(encoding="utf-8")
    salida_real = sys.stdout            # el código del alumno escribe en otro buffer
    pedido = json.load(sys.stdin)
    respuesta = atender(pedido)
    salida_real.write(json.dumps(respuesta, ensure_ascii=False))
    salida_real.flush()


if __name__ == "__main__":
    main()
