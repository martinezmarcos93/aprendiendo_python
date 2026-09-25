"""
Validador automático del contenido de los cursos.

Revisa TODO lo que un chico va a ver, sin abrir la app:
- ERROR (bloquea): estructura inválida, código que no corre, respuesta marcada como
  correcta que no lo es, palabra de TortuScript usada antes de enseñarla.
- AVISO (revisar): "Forma" repetida, consignas largas, jerga técnica, palabras que
  suelen escribirse sin tilde, orden de líneas ambiguo.

Uso: validar_curso(curso) -> list[Hallazgo];  herramientas/validar_contenido.py lo imprime.
"""
import itertools
import re
from dataclasses import dataclass

from .contenido import HUECO, TIPOS, pasos
from .evaluacion import normalizar_salida
from .executor import ejecutar_codigo
from .translator import TraductorTortuScript

ERROR, AVISO = "error", "aviso"

# Palabras de TortuScript que no hace falta "presentar" con una Forma: se entienden solas
_SIN_PRESENTACION = {"verdadero", "falso"}

JERGA = ("string", "float", "integer", "booleano", "sintaxis", "compilar", "iterar",
         "iteración", "parámetro", "argumento", "concatenar", "indentación", "array")

# Palabras que muy seguido se escriben sin la tilde que llevan
SIN_TILDE = {"renglon": "renglón", "veras": "verás", "linea": "línea", "numero": "número",
             "despues": "después", "tambien": "también", "facil": "fácil", "dificil": "difícil",
             "funcion": "función", "ultimo": "último", "codigo": "código", "pagina": "página"}

MAX_CARACTERES = 200
MAX_PALABRAS_FRASE = 25


@dataclass
class Hallazgo:
    nivel: str
    donde: str
    mensaje: str

    def __str__(self):
        icono = "❌" if self.nivel == ERROR else "⚠️ "
        return f"{icono} {self.donde}: {self.mensaje}"


def _correr(codigo_tortu, entradas=None):
    """Traduce y ejecuta. Devuelve (salida_programa, error, palabras_usadas)."""
    t = TraductorTortuScript()
    python = t.traducir_codigo(codigo_tortu)
    detalles = {}
    _, hay_error, mensaje = ejecutar_codigo(python, entradas_fijas=list(entradas or []), detalles=detalles)
    primera = mensaje.split("\n")[0] if hay_error else ""
    return detalles.get("salida_programa", ""), primera, list(t.ultimas_palabras)


def _palabras(codigo_tortu):
    t = TraductorTortuScript()
    t.traducir_codigo(codigo_tortu or "")
    return set(t.ultimas_palabras)


def _textos_del_paso(paso):
    campos = ("texto", "consigna", "pregunta", "nota")
    return [paso[c] for c in campos if isinstance(paso.get(c), str)]


def _revisar_texto(texto, donde, hallazgos):
    if len(texto) > MAX_CARACTERES:
        hallazgos.append(Hallazgo(AVISO, donde, f"texto largo ({len(texto)} caracteres, ideal ≤ {MAX_CARACTERES})"))
    for frase in re.split(r"[.!?]\s+", texto):
        n = len(frase.split())
        if n > MAX_PALABRAS_FRASE:
            hallazgos.append(Hallazgo(AVISO, donde, f"frase de {n} palabras: «{frase[:50]}…»"))
    fuera_de_codigo = re.sub(r'"[^"]*"|\([^)]*\)', " ", texto)
    for palabra in re.findall(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]+", fuera_de_codigo):
        p = palabra.lower()
        if p in JERGA:
            hallazgos.append(Hallazgo(AVISO, donde, f"jerga técnica: «{palabra}»"))
        if p in SIN_TILDE:
            hallazgos.append(Hallazgo(AVISO, donde, f"«{palabra}» suele llevar tilde: «{SIN_TILDE[p]}»"))


def _requeridos(paso, campos, donde, hallazgos):
    faltan = [c for c in campos if paso.get(c) in (None, "", [])]
    for c in faltan:
        hallazgos.append(Hallazgo(ERROR, donde, f"falta el campo «{c}»"))
    return not faltan


def _validar_paso(paso, donde, hallazgos):
    """Revisa un paso. Devuelve las palabras de TortuScript que usa su código."""
    tipo = paso.get("tipo")
    entradas = paso.get("entradas_prueba")
    usadas = set()

    if tipo == "explicacion":
        if _requeridos(paso, ["texto"], donde, hallazgos) and paso.get("codigo"):
            _, err, usadas = _correr(paso["codigo"], entradas)
            if err:
                hallazgos.append(Hallazgo(ERROR, donde, f"el ejemplo no corre: {err}"))

    elif tipo in ("elegir", "predecir"):
        campos = ["opciones", "correcta"] + (["pregunta"] if tipo == "elegir" else ["codigo"])
        if not _requeridos(paso, campos, donde, hallazgos):
            return set()
        opciones, correcta = paso["opciones"], paso["correcta"]
        if len(opciones) < 2:
            hallazgos.append(Hallazgo(ERROR, donde, "hace falta al menos 2 opciones"))
        if len(set(map(str, opciones))) != len(opciones):
            hallazgos.append(Hallazgo(ERROR, donde, "hay opciones repetidas"))
        if not isinstance(correcta, int) or not 0 <= correcta < len(opciones):
            hallazgos.append(Hallazgo(ERROR, donde, f"«correcta» fuera de rango: {correcta!r}"))
            return set()
        if tipo == "predecir":
            salida, err, usadas = _correr(paso["codigo"], entradas)
            if err:
                hallazgos.append(Hallazgo(ERROR, donde, f"el código no corre: {err}"))
            else:
                real = normalizar_salida(salida)
                if normalizar_salida(str(opciones[correcta])) != real:
                    hallazgos.append(Hallazgo(ERROR, donde, f"la opción correcta dice {opciones[correcta]!r} pero el código muestra {salida.strip()!r}"))
                otras = [o for i, o in enumerate(opciones) if i != correcta and normalizar_salida(str(o)) == real]
                if otras:
                    hallazgos.append(Hallazgo(ERROR, donde, f"otra opción también es correcta: {otras}"))
        elif paso.get("codigo"):
            _, err, usadas = _correr(paso["codigo"], entradas)
            if err:
                hallazgos.append(Hallazgo(ERROR, donde, f"el código de la pregunta no corre: {err}"))

    elif tipo == "completar":
        if not _requeridos(paso, ["consigna", "codigo", "fichas", "respuesta"], donde, hallazgos):
            return set()
        huecos, respuesta = paso["codigo"].count(HUECO), paso["respuesta"]
        if huecos != len(respuesta):
            hallazgos.append(Hallazgo(ERROR, donde, f"{huecos} huecos pero {len(respuesta)} respuestas"))
            return set()
        faltantes = [r for r in respuesta if r not in paso["fichas"]]
        if faltantes:
            hallazgos.append(Hallazgo(ERROR, donde, f"respuestas que no están entre las fichas: {faltantes}"))
        codigo = paso["codigo"]
        for r in respuesta:
            codigo = codigo.replace(HUECO, r, 1)
        salida, err, usadas = _correr(codigo, entradas)
        if err:
            hallazgos.append(Hallazgo(ERROR, donde, f"completado con la respuesta, no corre: {err}"))
        elif "salida" in paso and normalizar_salida(salida) != normalizar_salida(paso["salida"]):
            hallazgos.append(Hallazgo(ERROR, donde, f"muestra {salida.strip()!r} y se esperaba {paso['salida']!r}"))

    elif tipo == "ordenar":
        if not _requeridos(paso, ["consigna", "lineas"], donde, hallazgos):
            return set()
        lineas = paso["lineas"]
        if len(lineas) < 2:
            hallazgos.append(Hallazgo(ERROR, donde, "hace falta al menos 2 líneas para ordenar"))
            return set()
        salida, err, usadas = _correr("\n".join(lineas), entradas)
        if err:
            hallazgos.append(Hallazgo(ERROR, donde, f"en el orden correcto no corre: {err}"))
        elif not salida.strip():
            hallazgos.append(Hallazgo(ERROR, donde, "en el orden correcto no muestra nada"))
        elif len(lineas) <= 6:
            objetivo = normalizar_salida(salida)
            for orden in itertools.permutations(lineas):
                if list(orden) == lineas:
                    continue
                s, e, _ = _correr("\n".join(orden), entradas)
                if not e and normalizar_salida(s) == objetivo:
                    hallazgos.append(Hallazgo(AVISO, donde, "hay otro orden que muestra lo mismo; aceptá los dos al evaluar"))
                    break

    elif tipo == "escribir":
        if not _requeridos(paso, ["consigna", "solucion"], donde, hallazgos):
            return set()
        salida, err, usadas = _correr(paso["solucion"], entradas)
        usadas = set(usadas)
        if "preguntar" in usadas and not entradas:
            hallazgos.append(Hallazgo(ERROR, donde, "la solución usa preguntar: agregá «entradas_prueba»"))
        if err:
            hallazgos.append(Hallazgo(ERROR, donde, f"la solución no corre: {err}"))
        elif not salida.strip():
            hallazgos.append(Hallazgo(ERROR, donde, "la solución no muestra nada (no se podría evaluar)"))
    else:
        hallazgos.append(Hallazgo(ERROR, donde, f"tipo de paso desconocido: {tipo!r} (válidos: {', '.join(TIPOS)})"))
    return set(usadas)


def validar_curso(curso):
    hallazgos = []
    # ── estructura ──
    if not curso.get("secciones"):
        return [Hallazgo(ERROR, curso.get("id", "curso"), "el curso no tiene secciones")]
    vistos = {"sección": set(), "lección": set()}      # cada tipo tiene su propio espacio de ids
    for s in curso["secciones"]:
        for clave, valor in (("sección", s.get("id")),) + tuple(("lección", l.get("id")) for l in s.get("lecciones", [])):
            if valor in vistos[clave]:
                hallazgos.append(Hallazgo(ERROR, str(valor), f"id de {clave} repetido"))
            vistos[clave].add(valor)
        if not s.get("lecciones"):
            hallazgos.append(Hallazgo(ERROR, s.get("id", "?"), "sección sin lecciones"))

    # ── cada paso, en el orden en que lo vive el chico ──
    presentadas = {}          # palabra → dónde se presentó
    for seccion, leccion, i, paso in pasos(curso):
        donde = f"{leccion.get('titulo', leccion.get('id'))} · paso {i + 1} ({paso.get('tipo')})"
        for texto in _textos_del_paso(paso):
            _revisar_texto(texto, donde, hallazgos)

        nuevas = set()
        if paso.get("forma"):
            nuevas = _palabras(paso["forma"]) - _SIN_PRESENTACION
            if nuevas and all(p in presentadas for p in nuevas):
                # La Forma no enseña nada nuevo (si presenta algo nuevo, lo viejo va de paso)
                hallazgos.append(Hallazgo(AVISO, donde, "esta Forma no presenta nada nuevo: "
                                          + ", ".join(f"«{p}» ya se mostró en {presentadas[p]}" for p in sorted(nuevas))))
        if paso.get("tipo") == "explicacion" and paso.get("codigo"):
            nuevas |= _palabras(paso["codigo"]) - _SIN_PRESENTACION

        usadas = _validar_paso(paso, donde, hallazgos) - _SIN_PRESENTACION
        sin_presentar = sorted(usadas - set(presentadas) - nuevas)
        if sin_presentar:
            hallazgos.append(Hallazgo(ERROR, donde, f"usa {', '.join(sin_presentar)} antes de enseñarlo (falta una Forma o una explicación)"))
        for p in nuevas | usadas:
            presentadas.setdefault(p, donde)
    return hallazgos
