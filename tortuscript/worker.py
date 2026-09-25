"""
Proceso hijo que ejecuta UN pedido y termina. Lo lanza tortuscript.proceso.

Lee un JSON por stdin y escribe un JSON por stdout. Así el código del chico corre
aislado del servidor web, con límites de tiempo y memoria puestos por el padre.

Pedido:
  {"op": "ejecutar", "fuente": "...", "entradas": [...]}
  {"op": "evaluar",  "fuente": "...", "entradas": [...], "solucion": "..."}
"""
import json
import sys

from .evaluacion import evaluar
from .executor import ejecutar_codigo
from .translator import TraductorTortuScript, detectar_tipo


def _python_de(fuente):
    tipo = detectar_tipo(fuente)
    python = fuente if tipo == "python" else TraductorTortuScript().traducir_codigo(fuente)
    return tipo, python


def atender(pedido):
    tipo, python = _python_de(pedido.get("fuente", ""))
    detalles = {}
    salida, hay_error, mensaje = ejecutar_codigo(
        python, entradas_fijas=list(pedido.get("entradas") or []),
        detalles=detalles, completar_con_vacio=False)
    respuesta = {
        "tipo": tipo, "python": python,
        "salida": salida, "error": hay_error, "mensaje": mensaje,
        "salida_programa": detalles.get("salida_programa", ""),
        "entradas": detalles.get("entradas", []),
        "pregunta": detalles.get("pregunta_pendiente"),
    }
    if pedido.get("op") == "evaluar" and not hay_error and respuesta["pregunta"] is None:
        respuesta["evaluacion"] = evaluar(pedido.get("solucion", ""), detalles)
    return respuesta


def main():
    salida_real = sys.stdout            # el código del alumno escribe en otro buffer
    pedido = json.load(sys.stdin)
    respuesta = atender(pedido)
    salida_real.write(json.dumps(respuesta, ensure_ascii=False))
    salida_real.flush()


if __name__ == "__main__":
    main()
