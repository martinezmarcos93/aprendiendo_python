import re


class TraductorTortuScript:
    def __init__(self):
        # Patrones generales (mostrar se maneja aparte porque necesita paréntesis)
        self.patrones = [
            (r'clase\s+(\w+)\s+hereda\s+de\s+(\w+)\s*:', r'class \1(\2):'),
            (r'\bclase\b',    'class'),
            (r'\bfuncion\b',  'def'),
            (r'\bdevolver\b', 'return'),
            (r'repetir\s+(\d+)\s*veces\s*:', r'for _ in range(\1):'),
            (r'\bpara\b',     'for'),
            (r'\bmientras\b', 'while'),
            (r'\bsi\b',       'if'),
            (r'\bsino\b',     'else'),
            (r'\by\b',        'and'),
            (r'\bo\b',        'or'),
            (r'\bno\b',       'not'),
            (r'\bpreguntar\b','input'),
            (r'\bVerdadero\b','True'),
            (r'\bFalso\b',    'False'),
        ]

        self.asignacion_re = re.compile(r'\bes\b')
        self._mostrar_re   = re.compile(r'^mostrar\b(.*)')

    # ── Proteger strings de ser modificados por los patrones
    def _proteger_cadenas(self, linea):
        cadenas = []
        def reemplazar(match):
            cadenas.append(match.group(0))
            return f'__STR{len(cadenas)-1}__'
        linea = re.sub(r'"[^"\\]*(\\.[^"\\]*)*"', reemplazar, linea)
        linea = re.sub(r"'[^'\\]*(\\.[^'\\]*)*'", reemplazar, linea)
        return linea, cadenas

    def _restaurar_cadenas(self, linea, cadenas):
        for i, s in enumerate(cadenas):
            linea = linea.replace(f'__STR{i}__', s)
        return linea

    def _aplicar_patrones(self, texto):
        for patron, reemplazo in self.patrones:
            texto = re.sub(patron, reemplazo, texto)
        return texto

    def traducir_linea(self, linea_original):
        stripped = linea_original.strip()
        if stripped.startswith('#') or stripped == '':
            return linea_original

        # Preservar indentación
        indentacion = ''
        for c in linea_original:
            if c == ' ':
                indentacion += ' '
            else:
                break

        linea = stripped
        linea, cadenas = self._proteger_cadenas(linea)

        # mostrar expr  →  print(expr)   [manejo especial para agregar paréntesis]
        m = self._mostrar_re.match(linea)
        if m:
            argumento = m.group(1).strip()
            argumento = self._aplicar_patrones(argumento)
            argumento = self.asignacion_re.sub('=', argumento)
            argumento = self._restaurar_cadenas(argumento, cadenas)
            return indentacion + f'print({argumento})'

        linea = self._aplicar_patrones(linea)
        linea = self.asignacion_re.sub('=', linea)
        linea = self._restaurar_cadenas(linea, cadenas)
        return indentacion + linea

    def traducir_codigo(self, codigo_fuente):
        return '\n'.join(self.traducir_linea(l) for l in codigo_fuente.split('\n'))


# ──────────────────────────────────────────
# DETECTOR DE TIPO DE CÓDIGO
# ──────────────────────────────────────────

# Palabras que solo existen en TortuScript
_PALABRAS_TORTU = {
    "mostrar", "preguntar", "funcion", "devolver",
    "repetir", "veces", "mientras", "sino",
    "Verdadero", "Falso", "es",
}

# Palabras que son Python puro
_PALABRAS_PYTHON = {
    "print", "input", "def", "return",
    "for", "while", "range", "True", "False",
    "import", "class", "lambda", "yield",
}


def detectar_tipo(codigo):
    """
    Retorna 'tortuscript', 'python' o 'mixto'.
    Sirve para decidir si traducir o ejecutar directamente.
    """
    import re
    tokens = set(re.findall(r'\b\w+\b', codigo))

    tiene_tortu  = bool(tokens & _PALABRAS_TORTU)
    tiene_python = bool(tokens & _PALABRAS_PYTHON)

    # Si usa = sin "es", y no tiene palabras tortu → probablemente Python
    usa_asignacion_python = bool(re.search(r'(?<![=!<>])=(?!=)', codigo))
    usa_es = bool(re.search(r'\bes\b', codigo))
    if usa_asignacion_python and not usa_es and not tiene_tortu:
        tiene_python = True

    if tiene_tortu and not tiene_python:
        return "tortuscript"
    if tiene_python and not tiene_tortu:
        return "python"
    if tiene_tortu and tiene_python:
        return "mixto"
    return "tortuscript"
