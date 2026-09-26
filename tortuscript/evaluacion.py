"""
Evaluación de ejercicios, sin interfaz (la usa la app web).

Se compara lo que MUESTRA el programa del chico con lo que muestra la solución
oficial ejecutada con las mismas respuestas a preguntar(): cualquier forma de llegar
al mismo resultado es válida.
"""
import re

from . import tortuga
from .executor import ejecutar_codigo
from .translator import TraductorTortuScript, detectar_tipo

CORRECTO = "correcto"
INCORRECTO = "incorrecto"
SIN_SALIDA = "sin_salida"
FALTA_PREGUNTAR = "falta_preguntar"
SIN_DIBUJO = "sin_dibujo"
CHOQUE = "choque"                 # laberinto: la tortuga tocó una pared
NO_LLEGA = "no_llega"             # laberinto: terminó lejos de la salida
FALTA_USAR = "falta_usar"         # llegó, pero sin usar lo que pide el paso (p. ej. repetir)

# Semilla del azar de dado() al evaluar y al validar (ADR-009): el programa del chico y la solución oficial
# tiran los mismos números, así cualquier forma de llegar al mismo resultado es válida.
SEMILLA_EVALUACION = 2026

# (estrellas, xp) según cuántas pistas se vieron: 0, 1, 2, 3 (solución)
_PREMIOS = [(3, 30), (2, 20), (1, 10), (1, 5)]


def normalizar_salida(texto):
    """Compara lo que importa, no el tipeo:
    - ignora espacios al principio/final de línea y líneas vacías al final;
    - varios espacios seguidos cuentan como uno;
    - ignora espacios alrededor de signos: "7+3" == "7 + 3", "es:pizza" == "es: pizza".
    Sigue siendo estricto con palabras, mayúsculas y tildes ("Holamundo" != "Hola mundo")."""
    lineas = []
    for linea in (texto or "").strip().split("\n"):
        linea = re.sub(r"\s+", " ", linea.strip())
        linea = re.sub(r"\s*([^\w\s])\s*", r"\1", linea)
        lineas.append(linea)
    return "\n".join(lineas)


def estrellas_por_pistas(pistas_vistas):
    return _PREMIOS[min(max(pistas_vistas, 0), len(_PREMIOS) - 1)]


def palabras_clave(solucion):
    """Palabras de TortuScript que usa de verdad la solución (para la pista 1)."""
    t = TraductorTortuScript()
    t.traducir_codigo(solucion)
    palabras = [p for p in t.ultimas_palabras if p not in ("verdadero", "falso")]
    return palabras or ["mostrar"]


def evaluar(solucion, detalles_alumno, semilla=SEMILLA_EVALUACION):
    """Evalúa una ejecución YA hecha del alumno.

    `detalles_alumno` es el dict que completa ejecutar_codigo(..., detalles=...).
    Devuelve {'estado', 'esperado', 'obtenido'} con las salidas normalizadas.
    """
    entradas = detalles_alumno.get("entradas", [])
    traductor = TraductorTortuScript()
    en_python = detectar_tipo(solucion) == "python"             # los ejercicios del curso puente
    python_sol = solucion.strip() if en_python else traductor.traducir_codigo(solucion.strip())
    obtenido = normalizar_salida(detalles_alumno.get("salida_programa", ""))
    pregunta = "input(" in solucion if en_python else "preguntar" in traductor.ultimas_palabras

    if pregunta and not entradas:
        return {"estado": FALTA_PREGUNTAR, "esperado": "", "obtenido": obtenido}

    det_sol = {}
    ejecutar_codigo(python_sol, entradas_fijas=entradas, detalles=det_sol, semilla=semilla)
    esperado = normalizar_salida(det_sol.get("salida_programa", ""))

    if not obtenido:
        estado = SIN_SALIDA
    elif obtenido == esperado:
        estado = CORRECTO
    else:
        estado = INCORRECTO
    return {"estado": estado, "esperado": esperado, "obtenido": obtenido}


def ordenes_de(fuente, entradas=None, semilla=SEMILLA_EVALUACION):
    """Corre un programa de tortuga y devuelve sus órdenes (o None si falla o pregunta algo)."""
    traductor = TraductorTortuScript()
    registro = tortuga.Registro()
    detalles = {}
    _, hay_error, _ = ejecutar_codigo(
        fuente.strip() if detectar_tipo(fuente) == "python" else traductor.traducir_codigo(fuente.strip()), entradas_fijas=list(entradas or []), detalles=detalles,
        extra_globals=registro.globales(), callback_linea=registro.callback_linea, semilla=semilla)
    if hay_error or detalles.get("pregunta_pendiente") is not None:
        return None
    return registro.ordenes


def evaluar_dibujo(solucion, ordenes_alumno, entradas=None, semilla=SEMILLA_EVALUACION):
    """Compara el dibujo del alumno con el de la solución oficial. Devuelve
    {'estado', 'similitud', 'objetivo'}: `objetivo` son las órdenes de la solución."""
    objetivo = ordenes_de(solucion, entradas, semilla) or []
    if not tortuga.trazos(ordenes_alumno):
        return {"estado": SIN_DIBUJO, "similitud": 0.0, "objetivo": objetivo}
    similitud = tortuga.similitud(ordenes_alumno, objetivo)
    estado = CORRECTO if tortuga.mismo_dibujo(ordenes_alumno, objetivo) else INCORRECTO
    return {"estado": estado, "similitud": round(similitud, 3), "objetivo": objetivo}


def evaluar_laberinto(ordenes_alumno, laberinto, palabras_usadas=(), usar=()):
    """Evalúa un paso de laberinto: no hay dibujo objetivo, se comprueban las reglas del mundo
    (no tocar paredes y terminar en la salida). `usar`: palabras que el paso exige (p. ej. repetir).
    Devuelve {'estado', 'linea', 'ordenes'}; `ordenes` llega hasta el choque, si lo hubo."""
    r = tortuga.recorrer_laberinto(ordenes_alumno, laberinto)
    if r["estado"] == tortuga.CHOCO:
        estado = CHOQUE
    elif r["estado"] == tortuga.NO_LLEGO:
        estado = NO_LLEGA
    elif any(p not in palabras_usadas for p in usar):
        estado = FALTA_USAR
    else:
        estado = CORRECTO
    return {"estado": estado, "linea": r["linea"], "ordenes": r["ordenes"],
            "usar": [p for p in usar if p not in palabras_usadas]}
