"""
Traductor TortuScript → Python basado en tokens (módulo `tokenize` de la stdlib).

Por qué tokens y no regex: el tokenizador ya sabe qué es un string, un comentario,
un número o un nombre, así que las palabras clave solo se traducen donde de verdad
son palabras clave. Eso permite, por ejemplo, que `y`, `o`, `no` o `color` sigan
funcionando como nombres de variables.

Reglas principales:
- Se traduce línea por línea y cada línea de TortuScript da exactamente una línea de
  Python (así los números de línea de los errores coinciden con lo que escribió el chico).
- Las palabras clave aceptan tildes y mayúsculas: `función`, `Mostrar`, `SI`.
- La indentación se conserva; los tabs se convierten a 4 espacios.
"""
import io
import keyword
import tokenize
import unicodedata

_FSTRING_START = getattr(tokenize, "FSTRING_START", None)   # Python 3.12+
_FSTRING_END = getattr(tokenize, "FSTRING_END", None)

# Palabras que se reemplazan 1 a 1 (clave normalizada → Python)
SIMPLES = {
    "funcion": "def",
    "devolver": "return",
    "clase": "class",
    "mientras": "while",
    "verdadero": "True",
    "falso": "False",
}

# Comandos que llevan paréntesis automáticos: `mostrar "hola"` → `print("hola")`
COMANDOS = {
    "mostrar": "print",
    "avanzar": "avanzar",
    "retroceder": "retroceder",
    "girar_der": "girar_der",
    "girar_izq": "girar_izq",
    "color": "color",
    "bajar_lapiz": "bajar_lapiz",
    "subir_lapiz": "subir_lapiz",
}

# Palabras propias de TortuScript (normalizadas) — para detectar_tipo y las pistas
PALABRAS_TORTU = (
    set(SIMPLES) | set(COMANDOS)
    | {"preguntar", "repetir", "veces", "si", "sino", "para", "en", "es",
       "y", "o", "no", "hereda", "de"}
)

PALABRAS_PYTHON = {
    "print", "input", "def", "return", "for", "while", "range", "True", "False",
    "import", "class", "lambda", "yield", "elif", "if", "else", "in", "and", "or", "not",
}

_INICIO_OPERANDO_OP = {"(", "[", "{", "-", "+", "~"}
_FIN_OPERANDO_OP = {")", "]", "}"}


# Formas del voseo que un chico escribe naturalmente ("mostrá" en vez de "mostrar")
ALIAS = {
    "mostra": "mostrar",
}


def normalizar(palabra):
    """Minúsculas, sin tildes y con alias: 'Función' → 'funcion', 'Mostrá' → 'mostrar'."""
    sin_tildes = unicodedata.normalize("NFKD", palabra)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c)).lower()
    return ALIAS.get(sin_tildes, sin_tildes)


def _tokens_de_linea(texto):
    """Tokens significativos de una línea (sin indentación) y si quedó incompleta.
    Nunca levanta: si hay un string o paréntesis sin cerrar devuelve los tokens
    que se pudieron leer hasta ese punto."""
    tokens = []
    incompleta = False
    try:
        for t in tokenize.generate_tokens(io.StringIO(texto).readline):
            if t.type in (tokenize.NEWLINE, tokenize.NL, tokenize.ENDMARKER,
                          tokenize.INDENT, tokenize.DEDENT):
                continue
            if t.start[0] != 1:   # solo nos interesa la primera línea física
                break
            tokens.append(t)
    except (tokenize.TokenError, SyntaxError):
        incompleta = True
    return tokens, incompleta


class _Linea:
    """Una línea en traducción: tokens + lista de ediciones sobre el texto original."""

    def __init__(self, texto):
        self.texto = texto
        self.tokens, self.incompleta = _tokens_de_linea(texto)
        self.ediciones = []          # (inicio, fin, reemplazo) en columnas de `texto`
        self.en_fstring = self._marcar_fstrings()

    def _marcar_fstrings(self):
        dentro, nivel = [], 0
        for t in self.tokens:
            if _FSTRING_START is not None and t.type == _FSTRING_START:
                nivel += 1
            dentro.append(nivel > 0)
            if _FSTRING_END is not None and t.type == _FSTRING_END:
                nivel -= 1
        return dentro

    def es_nombre(self, i):
        return (0 <= i < len(self.tokens) and self.tokens[i].type == tokenize.NAME
                and not self.en_fstring[i])

    def norm(self, i):
        return normalizar(self.tokens[i].string) if self.es_nombre(i) else None

    def reemplazar(self, i, nuevo):
        t = self.tokens[i]
        self.ediciones.append((t.start[1], t.end[1], nuevo))

    def aplicar(self):
        salida = self.texto
        for ini, fin, nuevo in sorted(self.ediciones, key=lambda e: (e[0], e[1]), reverse=True):
            salida = salida[:ini] + nuevo + salida[fin:]
        return salida


class TraductorTortuScript:
    def __init__(self):
        self.ultimas_palabras = []   # palabras TortuScript usadas en la última traducción

    # ───────────────────────── API pública ─────────────────────────
    def traducir_codigo(self, codigo_fuente):
        self.ultimas_palabras = []
        return "\n".join(self._traducir(l) for l in codigo_fuente.split("\n"))

    def traducir_linea(self, linea_original):
        return self._traducir(linea_original)

    # ───────────────────────── Núcleo ─────────────────────────
    def _usar(self, palabra):
        if palabra not in self.ultimas_palabras:
            self.ultimas_palabras.append(palabra)

    def _traducir(self, linea_original):
        cuerpo = linea_original.lstrip(" \t")
        indentacion = linea_original[:len(linea_original) - len(cuerpo)].expandtabs(4)
        if not cuerpo.strip() or cuerpo.startswith("#"):
            return indentacion + cuerpo
        linea = _Linea(cuerpo)
        if linea.tokens:
            self._traducir_sentencias(linea)
        return indentacion + linea.aplicar()

    def _traducir_sentencias(self, linea):
        """Una línea puede tener varias sentencias: `si x: mostrar x` o `a es 1; b es 2`."""
        inicio = 0
        n = len(linea.tokens)
        while inicio < n:
            fin = self._fin_de_sentencia(linea, inicio)
            siguiente = self._traducir_sentencia(linea, inicio, fin)
            inicio = siguiente if siguiente is not None else fin + 1

    def _fin_de_sentencia(self, linea, inicio):
        """Índice del token donde termina la sentencia (exclusivo): `;`, comentario o fin."""
        profundidad = 0
        for i in range(inicio, len(linea.tokens)):
            t = linea.tokens[i]
            if t.type == tokenize.COMMENT:
                return i
            if t.type == tokenize.OP and not linea.en_fstring[i]:
                if t.string in "([{":
                    profundidad += 1
                elif t.string in ")]}":
                    profundidad -= 1
                elif t.string == ";" and profundidad <= 0:
                    return i
        return len(linea.tokens)

    def _traducir_sentencia(self, linea, ini, fin):
        """Traduce tokens [ini, fin). Devuelve el índice desde donde seguir si la
        sentencia es un encabezado de bloque con cuerpo en la misma línea."""
        if ini >= fin:
            return None
        cabeza = linea.norm(ini)
        es_condicion = False
        cuerpo_desde = None      # para encabezados `algo: sentencia`

        if cabeza == "repetir":
            veces = next((i for i in range(ini + 1, fin) if linea.norm(i) == "veces"), None)
            if veces is not None and veces > ini + 1:
                self._usar("repetir")
                linea.ediciones.append((linea.tokens[ini].start[1], linea.tokens[ini + 1].start[1],
                                        "for _ in range("))
                linea.ediciones.append((linea.tokens[veces - 1].end[1], linea.tokens[veces].end[1], ")"))
                self._traducir_expresion(linea, ini + 1, veces, es_condicion=True)
                cuerpo_desde = self._dos_puntos(linea, veces + 1, fin)
                return cuerpo_desde
            # `repetir` mal formado: se deja para que Python avise
        elif cabeza == "para":
            self._usar("para")
            linea.reemplazar(ini, "for")
            en = next((i for i in range(ini + 1, fin) if linea.norm(i) == "en"), None)
            if en is not None:
                linea.reemplazar(en, "in")
                self._traducir_expresion(linea, en + 1, fin, es_condicion=True)
            return self._dos_puntos(linea, ini + 1, fin)
        elif cabeza == "sino":
            self._usar("sino")
            if linea.norm(ini + 1) == "si":
                self._usar("si")
                linea.ediciones.append((linea.tokens[ini].start[1], linea.tokens[ini + 1].end[1], "elif"))
                self._traducir_expresion(linea, ini + 2, fin, es_condicion=True)
            else:
                linea.reemplazar(ini, "else")
            return self._dos_puntos(linea, ini + 1, fin)
        elif cabeza in ("si", "mientras"):
            self._usar(cabeza)
            linea.reemplazar(ini, "if" if cabeza == "si" else "while")
            es_condicion = True
            ini += 1
            cuerpo_desde = self._dos_puntos(linea, ini, fin)
        elif cabeza == "clase":
            self._usar("clase")
            linea.reemplazar(ini, "class")
            if linea.norm(ini + 2) == "hereda" and linea.norm(ini + 3) == "de":
                # `clase Perro hereda de Animal:` → `class Perro(Animal):`
                self._usar("hereda")
                linea.ediciones.append((linea.tokens[ini + 1].end[1], linea.tokens[ini + 4].start[1], "("))
                linea.ediciones.append((linea.tokens[ini + 4].end[1], linea.tokens[ini + 4].end[1], ")"))
            return self._dos_puntos(linea, ini + 1, fin)
        elif cabeza == "funcion":
            self._usar("funcion")
            linea.reemplazar(ini, "def")
            return self._dos_puntos(linea, ini + 1, fin)
        elif cabeza == "devolver":
            self._usar("devolver")
            linea.reemplazar(ini, "return")
            self._traducir_expresion(linea, ini + 1, fin, es_condicion=True)
            return None
        elif cabeza in COMANDOS and self._es_comando(linea, ini, fin):
            self._traducir_comando(linea, ini, fin)
            return None

        if es_condicion:
            limite = cuerpo_desde - 1 if cuerpo_desde is not None else fin
            self._traducir_expresion(linea, ini, limite, es_condicion=True)
            return cuerpo_desde

        # Sentencia común: asignación con `es` o expresión suelta
        self._traducir_expresion(linea, ini, fin, es_condicion=False)
        return None

    def _dos_puntos(self, linea, desde, fin):
        """Si hay `:` a nivel 0 y algo después, devuelve dónde empieza el cuerpo en línea."""
        profundidad = 0
        for i in range(desde, fin):
            t = linea.tokens[i]
            if t.type != tokenize.OP or linea.en_fstring[i]:
                continue
            if t.string in "([{":
                profundidad += 1
            elif t.string in ")]}":
                profundidad -= 1
            elif t.string == ":" and profundidad == 0:
                return i + 1 if i + 1 < fin else None
        return None

    def _es_comando(self, linea, i, fin):
        """`color "rojo"` es comando; `color es "rojo"` o `color = x` es una variable."""
        sig = i + 1
        if sig >= fin:
            return True                      # `mostrar` / `bajar_lapiz` solos
        t = linea.tokens[sig]
        if linea.norm(sig) == "es":
            return False
        if t.type == tokenize.OP and t.string in ("=", "+=", "-=", "*=", "/=", ".", "[", ",", ")"):
            return False
        return True

    def _traducir_comando(self, linea, i, fin):
        nombre = linea.norm(i)
        self._usar(nombre)
        destino = COMANDOS[nombre]
        sig = i + 1
        t_cmd = linea.tokens[i]
        if sig >= fin:
            if not linea.incompleta:          # `mostrar "sin cerrar`: que avise Python
                linea.reemplazar(i, destino + "()")
            return
        t_sig = linea.tokens[sig]
        cierra = self._cierre_de(linea, sig, fin) if t_sig.string == "(" else None
        if cierra == fin - 1:
            # Ya trae paréntesis que abarcan todo: `mostrar("hola")`
            linea.ediciones.append((t_cmd.start[1], t_sig.start[1], destino))
            self._traducir_expresion(linea, sig + 1, cierra, es_condicion=True)
            return
        linea.ediciones.append((t_cmd.start[1], t_sig.start[1], destino + "("))
        ultimo = linea.tokens[fin - 1]
        linea.ediciones.append((ultimo.end[1], ultimo.end[1], ")"))
        self._traducir_expresion(linea, sig, fin, es_condicion=True)

    def _cierre_de(self, linea, abre, fin):
        profundidad = 0
        for i in range(abre, fin):
            s = linea.tokens[i].string
            if linea.tokens[i].type != tokenize.OP:
                continue
            if s in "([{":
                profundidad += 1
            elif s in ")]}":
                profundidad -= 1
                if profundidad == 0:
                    return i
        return None

    # ───────────────────────── Expresiones ─────────────────────────
    def _es_operando_fin(self, linea, i):
        """¿El token i cierra un operando? (lo que puede ir a la izquierda de `y`/`o`)."""
        if i < 0:
            return False
        t = linea.tokens[i]
        if linea.en_fstring[i]:
            return _FSTRING_END is not None and t.type == _FSTRING_END
        if t.type in (tokenize.NUMBER, tokenize.STRING):
            return True
        if t.type == tokenize.OP:
            return t.string in _FIN_OPERANDO_OP
        if t.type == tokenize.NAME:
            n = normalizar(t.string)
            # y/o/no cuentan como operando (variable) salvo que ya se hayan convertido
            # a operador: eso lo controla quien llama con el conjunto `convertidos`.
            return n not in {"es", "si", "mientras", "devolver", "en",
                             "sino", "para", "veces", "mostrar", "preguntar"} and not keyword.iskeyword(t.string) \
                or t.string in ("True", "False", "None")
        return False

    def _es_operando_inicio(self, linea, i, fin):
        """¿El token i puede empezar un operando? (lo que puede ir a la derecha)."""
        if i >= fin:
            return False
        t = linea.tokens[i]
        if _FSTRING_START is not None and t.type == _FSTRING_START:
            return True
        if t.type in (tokenize.NUMBER, tokenize.STRING):
            return True
        if t.type == tokenize.OP:
            return t.string in _INICIO_OPERANDO_OP
        if t.type == tokenize.NAME:
            n = normalizar(t.string)
            if n in ("y", "o"):
                # `a y y < 2`: el segundo `y` es variable si lo que le sigue NO empieza
                # un operando (es un operador o el final).
                return not self._inicio_simple(linea, i + 1, fin)
            return n not in {"es", "veces", "en"} and t.string not in ("and", "or", "in", "is")
        return False

    def _inicio_simple(self, linea, i, fin):
        if i >= fin:
            return False
        t = linea.tokens[i]
        if t.type in (tokenize.NUMBER, tokenize.STRING):
            return True
        if _FSTRING_START is not None and t.type == _FSTRING_START:
            return True
        if t.type == tokenize.OP:
            return t.string in _INICIO_OPERANDO_OP
        if t.type == tokenize.NAME:
            return normalizar(t.string) not in {"y", "o", "es", "veces", "en"}
        return False

    def _traducir_expresion(self, linea, ini, fin, es_condicion):
        """Traduce palabras dentro de una expresión: y/o/no, es, verdadero/falso,
        preguntar. En una sentencia común, el primer `es` a nivel 0 es asignación
        (`=`); en condiciones o los siguientes, es comparación (`==`)."""
        profundidad = 0
        asignacion_hecha = es_condicion
        convertidos = set()          # índices ya convertidos a operador
        for i in range(ini, fin):
            t = linea.tokens[i]
            if linea.en_fstring[i]:
                continue
            if t.type == tokenize.OP:
                if t.string in "([{":
                    profundidad += 1
                elif t.string in ")]}":
                    profundidad -= 1
                elif t.string in ("=", "+=", "-=", "*=", "/=") and profundidad == 0:
                    asignacion_hecha = True
                continue
            if t.type != tokenize.NAME:
                continue
            n = normalizar(t.string)
            prev_ok = (i - 1 >= ini and (i - 1) not in convertidos and self._es_operando_fin(linea, i - 1))
            if n in ("y", "o"):
                if prev_ok and self._es_operando_inicio(linea, i + 1, fin):
                    linea.reemplazar(i, "and" if n == "y" else "or")
                    convertidos.add(i)
                    self._usar(n)
            elif n == "no":
                if not prev_ok and self._es_operando_inicio(linea, i + 1, fin):
                    linea.reemplazar(i, "not")
                    convertidos.add(i)
                    self._usar("no")
            elif n == "es":
                if i == ini or not self._es_operando_fin(linea, i - 1):
                    continue                  # `es` suelto: probablemente un nombre
                if not asignacion_hecha and profundidad == 0:
                    linea.reemplazar(i, "=")
                    asignacion_hecha = True
                else:
                    linea.reemplazar(i, "==")
                convertidos.add(i)
                self._usar("es")
            elif n in ("verdadero", "falso"):
                linea.reemplazar(i, SIMPLES[n])
                self._usar(n)
            elif n == "preguntar":
                self._usar("preguntar")
                sig = i + 1
                if sig < fin and linea.tokens[sig].string == "(":
                    linea.reemplazar(i, "input")
                elif sig < fin:
                    # `nombre es preguntar "¿Nombre?"` → `input("¿Nombre?")`
                    linea.ediciones.append((t.start[1], linea.tokens[sig].start[1], "input("))
                    ultimo = linea.tokens[fin - 1]
                    linea.ediciones.append((ultimo.end[1], ultimo.end[1], ")"))
                else:
                    linea.reemplazar(i, "input()")


# ──────────────────────────────────────────
# DETECTOR DE TIPO DE CÓDIGO
# ──────────────────────────────────────────
def detectar_tipo(codigo):
    """
    Retorna 'tortuscript', 'python' o 'mixto'.
    Solo mira nombres reales (ignora strings y comentarios).
    """
    nombres = set()
    asignacion_python = False
    for linea in codigo.split("\n"):
        cuerpo = linea.strip()
        if not cuerpo or cuerpo.startswith("#"):
            continue
        l = _Linea(cuerpo)
        for i, t in enumerate(l.tokens):
            if l.en_fstring[i]:
                continue
            if t.type == tokenize.NAME:
                nombres.add(t.string)
            elif t.type == tokenize.OP and t.string == "=":
                asignacion_python = True

    normalizados = {normalizar(n) for n in nombres}
    # palabras ambiguas que también son nombres comunes no deciden solas
    tortu_fuertes = PALABRAS_TORTU - {"y", "o", "no", "en", "de", "color"}
    tiene_tortu = bool(normalizados & tortu_fuertes)
    tiene_python = bool(nombres & PALABRAS_PYTHON) or (asignacion_python and not tiene_tortu)

    if tiene_tortu and tiene_python:
        return "mixto"
    if tiene_python:
        return "python"
    return "tortuscript"
