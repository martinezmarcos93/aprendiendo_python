"""
Motor de lecciones (sin interfaz): qué ve el chico de cada paso, cómo se comprueba
y cuánto vale. La UI (web) solo dibuja; toda la lógica está acá y tiene tests.

Tipos de paso (ver contenido.py): explicacion, elegir, completar, ordenar, predecir, escribir.

Reglas amables (nada de vidas ni castigos):
- Ante un error hay una pista específica; se puede reintentar todas las veces que haga falta.
- Después de 2 errores aparece "Ver respuesta": se ve y se sigue, sin XP en ese paso.
- XP por paso: 5 al primer intento, 2 si hubo reintentos, 0 si se vio la respuesta.
  Los pasos "escribir" siguen valiendo lo de siempre (30/20/10/5 según las pistas usadas).
- Una lección es "perfecta" si todos sus pasos salieron al primer intento y sin ver respuestas.
"""
import random
import zlib

from .contenido import HUECO
from .evaluacion import normalizar_salida

XP_PRIMER_INTENTO = 5
XP_REINTENTO = 2
ERRORES_PARA_VER_RESPUESTA = 2

PISTAS_GENERICAS = {
    "elegir": "Leé la pregunta otra vez y descartá las opciones que no pueden ser.",
    "predecir": "Seguí el código línea por línea, como si fueras la computadora.",
    "completar": "Mirá qué necesita cada hueco: una palabra, un texto o un número.",
    "ordenar": "Pensá qué tiene que pasar primero para que lo siguiente tenga sentido.",
}


# ─────────────────────────────────────────
# NAVEGACIÓN
# ─────────────────────────────────────────
def buscar_leccion(curso, leccion_id):
    """(seccion, leccion, posicion) o None. `posicion` es el orden dentro del curso (base 0)."""
    posicion = 0
    for seccion in curso["secciones"]:
        for leccion in seccion["lecciones"]:
            if leccion["id"] == leccion_id:
                return seccion, leccion, posicion
            posicion += 1
    return None


def lista_lecciones(curso):
    return [leccion for seccion in curso["secciones"] for leccion in seccion["lecciones"]]


def leccion_siguiente(curso, leccion_id):
    todas = lista_lecciones(curso)
    for i, leccion in enumerate(todas):
        if leccion["id"] == leccion_id:
            return todas[i + 1] if i + 1 < len(todas) else None
    return None


def esta_completada(progreso, leccion_id, indices_escribir):
    """Una lección cuenta como completada si se terminó en el motor de lecciones, o si es
    de las del formato viejo cuyos ejercicios 'escribir' ya estaban resueltos (así el progreso
    guardado antes del motor no se pierde)."""
    if progreso.get("lecciones", {}).get(leccion_id, {}).get("completada"):
        return True
    ejercicios = progreso.get("ejercicios", {})
    return bool(indices_escribir) and all(
        ejercicios.get(str(i), {}).get("completado") for i in indices_escribir)


# ─────────────────────────────────────────
# LO QUE VE EL CHICO (sin las respuestas)
# ─────────────────────────────────────────
def _semilla(leccion_id, indice):
    return zlib.crc32(f"{leccion_id}:{indice}".encode("utf-8"))


def _mezclar(elementos, semilla, distinto_del_original=False):
    """Mezcla reproducible (la página se ve igual al recargar). Si se pide, evita devolver
    el mismo orden que el original (para 'ordenar')."""
    mezclado = list(elementos)
    azar = random.Random(semilla)
    for _ in range(10):
        azar.shuffle(mezclado)
        if not distinto_del_original or mezclado != list(elementos) or len(set(elementos)) < 2:
            break
    return mezclado


def paso_publico(paso, leccion_id, indice, numero_ejercicio=None):
    """El paso tal como lo recibe el navegador. Nunca incluye la respuesta correcta."""
    tipo = paso["tipo"]
    semilla = _semilla(leccion_id, indice)
    publico = {"tipo": tipo, "indice": indice}
    if tipo == "explicacion":
        publico.update(texto=paso["texto"], codigo=paso.get("codigo"), forma=paso.get("forma"))
    elif tipo == "elegir":
        publico.update(pregunta=paso["pregunta"], codigo=paso.get("codigo"),
                       opciones=_mezclar([str(o) for o in paso["opciones"]], semilla))
    elif tipo == "predecir":
        publico.update(pregunta=paso.get("pregunta", "¿Qué va a mostrar este programa?"),
                       codigo=paso["codigo"],
                       opciones=_mezclar([str(o) for o in paso["opciones"]], semilla))
    elif tipo == "completar":
        publico.update(consigna=paso["consigna"], codigo=paso["codigo"],
                       fichas=_mezclar(paso["fichas"], semilla), huecos=paso["codigo"].count(HUECO))
    elif tipo == "ordenar":
        publico.update(consigna=paso["consigna"],
                       lineas=_mezclar(paso["lineas"], semilla, distinto_del_original=True))
    elif tipo == "escribir":
        publico.update(consigna=paso["consigna"], forma=paso.get("forma"), nota=paso.get("nota"),
                       ejercicio=numero_ejercicio)
    return publico


def respuesta_correcta(paso):
    """La respuesta para mostrar cuando el chico elige 'Ver respuesta'."""
    tipo = paso["tipo"]
    if tipo in ("elegir", "predecir"):
        return str(paso["opciones"][paso["correcta"]])
    if tipo == "completar":
        return list(paso["respuesta"])
    if tipo == "ordenar":
        return list(paso["lineas"])
    if tipo == "escribir":
        return paso["solucion"]
    return None


# ─────────────────────────────────────────
# COMPROBAR
# ─────────────────────────────────────────
def _completado(paso, rellenos):
    codigo = paso["codigo"]
    for r in rellenos:
        codigo = codigo.replace(HUECO, r, 1)
    return codigo


def _misma_salida(ejecutar, fuente_a, fuente_b, entradas):
    """True si ambos programas muestran lo mismo sin errores. `ejecutar(fuente, entradas)`
    devuelve lo que mostró el programa, o None si falló."""
    a, b = ejecutar(fuente_a, entradas), ejecutar(fuente_b, entradas)
    return a is not None and b is not None and normalizar_salida(a) != "" \
        and normalizar_salida(a) == normalizar_salida(b)


def comprobar(paso, respuesta, ejecutar=None):
    """Comprueba la respuesta a un paso que NO es 'escribir' (ese se evalúa ejecutando).

    respuesta: elegir/predecir → el texto de la opción; completar → lista de textos;
    ordenar → lista de líneas; explicacion → ignorada.
    `ejecutar` (opcional) permite aceptar otra forma válida de resolver 'completar' y
    'ordenar' cuando muestra lo mismo que la respuesta oficial.
    Devuelve {"ok": bool, "pista": str|None, "malos": [índices]|None}.
    """
    tipo = paso["tipo"]
    if tipo == "explicacion":
        return {"ok": True, "pista": None, "malos": None}

    if tipo in ("elegir", "predecir"):
        ok = isinstance(respuesta, str) and respuesta == str(paso["opciones"][paso["correcta"]])
        return {"ok": ok, "pista": None if ok else paso.get("pista") or PISTAS_GENERICAS[tipo], "malos": None}

    if tipo == "completar":
        esperado = paso["respuesta"]
        if not isinstance(respuesta, list) or len(respuesta) != len(esperado):
            return {"ok": False, "pista": "Todavía quedan huecos sin completar.", "malos": None}
        malos = [i for i, (r, e) in enumerate(zip(respuesta, esperado)) if r != e]
        if not malos:
            return {"ok": True, "pista": None, "malos": None}
        if ejecutar and all(isinstance(r, str) and r in paso["fichas"] for r in respuesta) \
                and paso.get("salida") is not None:
            salida = ejecutar(_completado(paso, respuesta), paso.get("entradas_prueba") or [])
            if salida is not None and normalizar_salida(salida) == normalizar_salida(paso["salida"]):
                return {"ok": True, "pista": None, "malos": None}
        return {"ok": False, "pista": paso.get("pista") or PISTAS_GENERICAS["completar"], "malos": malos}

    if tipo == "ordenar":
        esperado = paso["lineas"]
        if not isinstance(respuesta, list) or len(respuesta) != len(esperado):
            return {"ok": False, "pista": "Todavía faltan líneas por ubicar.", "malos": None}
        if respuesta == esperado:
            return {"ok": True, "pista": None, "malos": None}
        if ejecutar and sorted(respuesta) == sorted(esperado) and \
                _misma_salida(ejecutar, "\n".join(respuesta), "\n".join(esperado),
                              paso.get("entradas_prueba") or []):
            return {"ok": True, "pista": None, "malos": None}
        malos = [i for i, (r, e) in enumerate(zip(respuesta, esperado)) if r != e]
        return {"ok": False, "pista": paso.get("pista") or PISTAS_GENERICAS["ordenar"], "malos": malos}

    raise ValueError(f"tipo de paso sin comprobación directa: {tipo!r}")


# ─────────────────────────────────────────
# XP
# ─────────────────────────────────────────
def xp_por_intentos(intentos, vio_respuesta):
    """XP de un paso que no es 'escribir'."""
    if vio_respuesta:
        return 0
    return XP_PRIMER_INTENTO if intentos <= 1 else XP_REINTENTO


def puede_ver_respuesta(errores):
    return errores >= ERRORES_PARA_VER_RESPUESTA
