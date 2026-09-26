"""
Intereses y feedback locales (ADR-005): qué le gustaría crear al chico, para decidir qué construir después.

Todo queda en el progreso del perfil (campo `intereses`): no se manda a ningún lado. Solo opciones cerradas (sin texto
libre: un chico podría escribir datos personales). Se pregunta después de usar el producto, nunca en la bienvenida, y
"Ahora no" se respeta: no se vuelve a insistir.

Las encuestas son datos (`contenido/encuestas/*.json`) y se validan como los cursos.
Pura: no toca disco salvo al leer las encuestas; quien llama guarda el progreso.
"""
import json
from datetime import date
from functools import lru_cache
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent / "contenido" / "encuestas"
MOMENTOS = ("curso-terminado",)


@lru_cache(maxsize=None)
def cargar_encuestas():
    """{id: encuesta} de todas las encuestas."""
    salida = {}
    for archivo in sorted(CARPETA.glob("*.json")):
        with open(archivo, encoding="utf-8") as f:
            encuesta = json.load(f)
        salida[encuesta["id"]] = encuesta
    return salida


def problemas(encuesta):
    """Qué está mal en una encuesta (lista vacía si está bien)."""
    errores = []
    for campo in ("id", "pregunta", "opciones", "cuando"):
        if not encuesta.get(campo):
            errores.append(f"falta «{campo}»")
    if encuesta.get("cuando") and encuesta["cuando"] not in MOMENTOS:
        errores.append(f"«cuando» desconocido: {encuesta['cuando']!r}")
    ids = [o.get("id") for o in encuesta.get("opciones", [])]
    if len(ids) < 2:
        errores.append("hacen falta al menos 2 opciones")
    if len(set(ids)) != len(ids) or not all(ids):
        errores.append("hay opciones sin id o repetidas")
    if not all(o.get("texto") for o in encuesta.get("opciones", [])):
        errores.append("hay opciones sin texto")
    return errores


def pendiente(progreso, momento):
    """La primera encuesta de ese momento que el chico todavía no contestó ni dejó para después, o None."""
    ya = progreso.get("intereses") or {}
    return next((e for e in cargar_encuestas().values() if e["cuando"] == momento and e["id"] not in ya), None)


def responder(progreso, encuesta_id, respuestas, hoy=None):
    """Guarda lo elegido. Solo acepta opciones de esa encuesta (una sola si no es múltiple)."""
    encuesta = cargar_encuestas().get(encuesta_id)
    if encuesta is None:
        raise ValueError("Esa pregunta no existe.")
    validas = {o["id"] for o in encuesta["opciones"]}
    if not isinstance(respuestas, list) or not respuestas or not all(r in validas for r in respuestas):
        raise ValueError("Elegí al menos una opción.")
    if not encuesta.get("multiple") and len(respuestas) > 1:
        raise ValueError("Elegí una sola opción.")
    elegidas = [o["id"] for o in encuesta["opciones"] if o["id"] in respuestas]        # sin repetidos, en orden
    progreso.setdefault("intereses", {})[encuesta_id] = {"respuestas": elegidas, "fecha": str(hoy or date.today())}


def omitir(progreso, encuesta_id, hoy=None):
    """"Ahora no": queda anotado para no volver a preguntar."""
    if encuesta_id not in cargar_encuestas():
        raise ValueError("Esa pregunta no existe.")
    progreso.setdefault("intereses", {})[encuesta_id] = {"respuestas": [], "fecha": str(hoy or date.today()),
                                                         "omitida": True}


def limpiar(intereses):
    """Para importar un progreso: se queda solo con encuestas y opciones que existen."""
    encuestas, salida = cargar_encuestas(), {}
    for encuesta_id, dato in (intereses or {}).items():
        if encuesta_id not in encuestas or not isinstance(dato, dict):
            continue
        validas = {o["id"] for o in encuestas[encuesta_id]["opciones"]}
        respuestas = [r for r in dato.get("respuestas") or [] if isinstance(r, str) and r in validas]
        salida[encuesta_id] = {"respuestas": respuestas, "fecha": str(dato.get("fecha") or "")[:10]}
        if dato.get("omitida") is True:
            salida[encuesta_id]["omitida"] = True
    return salida
