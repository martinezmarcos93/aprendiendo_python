import re


class TraductorTortuScript:
    def __init__(self):
        self.patrones = [
            # estructuras
            (r'clase\s+(\w+)\s+hereda\s+de\s+(\w+)\s*:', r'class \1(\2):'),
            (r'\bclase\b', 'class'),
            (r'\bfuncion\b', 'def'),
            (r'\bdevolver\b', 'return'),

            # control
            (r'repetir\s+(\d+)\s*veces\s*:', r'for _ in range(\1):'),
            (r'\bpara\b', 'for'),
            (r'\bmientras\b', 'while'),
            (r'\bsi\b', 'if'),
            (r'\bsino\b', 'else'),

            # lógica
            (r'\by\b', 'and'),
            (r'\bo\b', 'or'),
            (r'\bno\b', 'not'),

            # funciones básicas
            (r'\bmostrar\b', 'print'),
            (r'\bpreguntar\b', 'input'),

            # booleanos
            (r'\bVerdadero\b', 'True'),
            (r'\bFalso\b', 'False'),
        ]

        self.asignacion_re = re.compile(r'\bes\b')

    # -------------------------
    # PROTEGER STRINGS
    # -------------------------
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

    # -------------------------
    # TRADUCIR UNA LÍNEA
    # -------------------------
    def traducir_linea(self, linea_original):
        if linea_original.strip().startswith("#") or linea_original.strip() == "":
            return linea_original

        # guardar indentación
        indentacion = ""
        for c in linea_original:
            if c == " ":
                indentacion += " "
            else:
                break

        linea = linea_original.strip()

        # proteger strings
        linea, cadenas = self._proteger_cadenas(linea)

        # aplicar reglas
        for patron, reemplazo in self.patrones:
            linea = re.sub(patron, reemplazo, linea)

        # asignación
        linea = self.asignacion_re.sub("=", linea)

        # restaurar strings
        linea = self._restaurar_cadenas(linea, cadenas)

        return indentacion + linea

    # -------------------------
    # TRADUCIR BLOQUE
    # -------------------------
    def traducir_codigo(self, codigo_fuente):
        lineas = codigo_fuente.split("\n")
        resultado = []

        for linea in lineas:
            traducida = self.traducir_linea(linea)
            resultado.append(traducida)

        return "\n".join(resultado)