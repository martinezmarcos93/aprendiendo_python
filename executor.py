"""
Ejecución del código del alumno.

Protecciones (sin dependencias externas):
- Validación del árbol de sintaxis (AST) ANTES de ejecutar: no se permite `import`
  ni nombres/atributos que empiecen con `_` (así se cierra la puerta clásica
  `().__class__.__base__.__subclasses__()` para llegar a `os`). `_` solo sí se permite.
- Builtins recortados.
- Límite TOTAL de pasos (líneas ejecutadas) para cortar bucles infinitos.
- Límite de caracteres de salida.

Límites conocidos: no hay tope de memoria (haría falta un subproceso) y no es un
sandbox apto para código hostil; está pensado para proteger a un chico de errores
y de copiar/pegar cosas peligrosas, no de un atacante.
"""
import ast
import io
import sys
import tkinter as tk
from tkinter import simpledialog

from error_handler import armar_mensaje_error

MAX_PASOS = 50_000
MAX_SALIDA = 20_000          # caracteres
ARCHIVO_ALUMNO = "<tu código>"


class BucleInfinito(Exception):
    """El código superó MAX_PASOS."""


class SalidaDemasiadoLarga(Exception):
    """El código mostró más de MAX_SALIDA caracteres."""


class CodigoNoPermitido(Exception):
    """El código usa algo que TortuScript no permite (import, nombres con _)."""

    def __init__(self, mensaje, linea=None):
        super().__init__(mensaje)
        self.linea = linea


# -------------------------
# VALIDACIÓN PREVIA (AST)
# -------------------------
def validar_codigo(codigo_python):
    """Levanta SyntaxError o CodigoNoPermitido. Devuelve el objeto de código compilado."""
    arbol = ast.parse(codigo_python, filename=ARCHIVO_ALUMNO)
    for nodo in ast.walk(arbol):
        linea = getattr(nodo, "lineno", None)
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            raise CodigoNoPermitido("En TortuScript no se pueden importar módulos.", linea)
        if isinstance(nodo, ast.Attribute) and nodo.attr.startswith("_"):
            raise CodigoNoPermitido(
                f"No se puede usar «.{nodo.attr}»: los nombres que empiezan con _ son internos de Python.",
                linea)
        if isinstance(nodo, ast.Name) and nodo.id.startswith("__"):
            raise CodigoNoPermitido(
                f"No se puede usar «{nodo.id}»: es un nombre interno de Python.", linea)
    return compile(arbol, ARCHIVO_ALUMNO, "exec")


# -------------------------
# SALIDA CON TOPE
# -------------------------
class _Salida(io.StringIO):
    """Guarda lo que muestra el programa. `pantalla` además incluye el eco de las
    respuestas a preguntar() (como en una terminal); `programa` solo lo de print."""

    def __init__(self):
        super().__init__()
        self.programa = io.StringIO()

    def write(self, texto):
        if self.tell() + len(texto) > MAX_SALIDA:
            raise SalidaDemasiadoLarga()
        self.programa.write(texto)
        return super().write(texto)

    def eco(self, texto):
        """Solo pantalla (prompts y respuestas de preguntar)."""
        return super().write(texto)


# -------------------------
# INPUT
# -------------------------
class InputInteractivo:
    """input() del alumno. Con `entradas_fijas` responde desde esa lista sin abrir
    diálogos (se usa para evaluar la solución oficial con las mismas respuestas)."""

    def __init__(self, salida, entradas_fijas=None, registro=None):
        self._salida = salida
        self._fijas = list(entradas_fijas) if entradas_fijas is not None else None
        self._registro = registro

    def __call__(self, prompt=""):
        if self._fijas is not None:
            respuesta = self._fijas.pop(0) if self._fijas else ""
        else:
            root = tk._default_root
            if not root:
                root = tk.Tk()
                root.withdraw()
            respuesta = simpledialog.askstring(
                "Entrada de datos", str(prompt) if prompt else "Ingresá un valor:", parent=root)
            if respuesta is None:
                respuesta = ""
        if self._registro is not None:
            self._registro.append(respuesta)
        self._salida.eco(f"{prompt}{respuesta}\n")
        return respuesta


# -------------------------
# ENTORNO
# -------------------------
def _hacer_globals(salida, entradas_fijas=None, registro=None):
    return {
        "__builtins__": {
            "print": print,
            "input": InputInteractivo(salida, entradas_fijas, registro),
            "range": range, "len": len, "int": int, "float": float, "str": str,
            "list": list, "dict": dict, "tuple": tuple, "set": set, "bool": bool,
            "True": True, "False": False, "None": None,
            "abs": abs, "min": min, "max": max, "sum": sum, "round": round,
            "type": type, "enumerate": enumerate, "zip": zip,
            "sorted": sorted, "reversed": reversed, "isinstance": isinstance,
            # para que `raise`/`try` y los mensajes funcionen normalmente
            "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
            "ZeroDivisionError": ZeroDivisionError, "IndexError": IndexError,
            "KeyError": KeyError, "NameError": NameError,
        }
    }


def _hacer_tracer(callback_linea):
    pasos = [0]

    def local(frame, event, arg):
        if event == "line":
            pasos[0] += 1
            if pasos[0] > MAX_PASOS:
                raise BucleInfinito()
            if callback_linea is not None:
                callback_linea(frame.f_lineno)
        return local

    def global_(frame, event, arg):
        # Solo se traza el código del alumno: ni tkinter, ni turtle, ni diálogos.
        if frame.f_code.co_filename == ARCHIVO_ALUMNO:
            return local
        return None

    return global_


# -------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------
def ejecutar_codigo(codigo_python, extra_globals=None, callback_linea=None,
                    entradas_fijas=None, detalles=None):
    """Ejecuta el código y devuelve (salida_pantalla, hubo_error, mensaje_error).

    - callback_linea(n): se llama antes de ejecutar cada línea n del alumno (depurador).
    - entradas_fijas: respuestas para preguntar() sin abrir diálogos.
    - detalles (dict opcional): se completa con 'salida_programa' (solo prints) y
      'entradas' (lo que se respondió a cada preguntar()).
    """
    salida = _Salida()
    registro_entradas = []
    stdout_original = sys.stdout
    try:
        codigo = validar_codigo(codigo_python)
        entorno = _hacer_globals(salida, entradas_fijas, registro_entradas)
        if extra_globals:
            entorno.update(extra_globals)
        sys.stdout = salida
        sys.settrace(_hacer_tracer(callback_linea))
        try:
            exec(codigo, entorno)
        finally:
            sys.settrace(None)
            sys.stdout = stdout_original
        resultado = (salida.getvalue(), False, "")
    except Exception as e:
        resultado = (salida.getvalue(), True, armar_mensaje_error(e, ARCHIVO_ALUMNO))
    finally:
        sys.settrace(None)
        sys.stdout = stdout_original
        if detalles is not None:
            detalles["salida_programa"] = salida.programa.getvalue()
            detalles["entradas"] = registro_entradas
    return resultado
