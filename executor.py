import sys
import io
import tkinter as tk
from tkinter import simpledialog
from error_handler import explicar_error

MAX_PASOS = 50_000


def _tracer(max_pasos):
    pasos = [0]
    def trace(frame, event, arg):
        pasos[0] += 1
        if pasos[0] > max_pasos:
            raise TimeoutError(
                f"El código ejecutó más de {max_pasos:,} instrucciones.\n"
                "¿Tenés un bucle infinito?"
            )
        return trace
    return trace


# -------------------------
# INPUT INTERACTIVO
# Usa simpledialog para pedir datos sin colgar la app
# -------------------------
class InputInteractivo:
    def __init__(self, salida_buffer):
        self._buf = salida_buffer

    def __call__(self, prompt=""):
        if prompt:
            self._buf.write(str(prompt))
            
        root = tk._default_root
        if not root:
            root = tk.Tk()
            root.withdraw()
            
        respuesta = simpledialog.askstring("Entrada de datos", prompt if prompt else "Ingresá un valor:", parent=root)
        if respuesta is None:
            respuesta = ""
            
        self._buf.write(str(respuesta) + "\n")
        return respuesta


# -------------------------
# ENTORNO SEGURO
# Se crea fresco en cada ejecución para
# evitar que variables de una corrida
# contaminen la siguiente.
# -------------------------
def _hacer_globals(salida_buffer):
    input_interactivo = InputInteractivo(salida_buffer)
    return {
        "__builtins__": {
            "print":  print,
            "input":  input_interactivo,
            "range":  range,
            "len":    len,
            "int":    int,
            "float":  float,
            "str":    str,
            "list":   list,
            "dict":   dict,
            "tuple":  tuple,
            "set":    set,
            "bool":   bool,
            "True":   True,
            "False":  False,
            "None":   None,
            "abs":    abs,
            "min":    min,
            "max":    max,
            "sum":    sum,
            "round":  round,
            "type":   type,
            "enumerate": enumerate,
            "zip":    zip,
        }
    }


# -------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------
def ejecutar_codigo(codigo_python):
    salida_capturada = io.StringIO()

    try:
        sys.stdout = salida_capturada

        # globals frescos por ejecución
        entorno = _hacer_globals(salida_capturada)
        
        # Iniciar protección contra bucles infinitos
        sys.settrace(_tracer(MAX_PASOS))
        
        exec(codigo_python, entorno)
        
        sys.settrace(None)
        sys.stdout = sys.__stdout__
        return salida_capturada.getvalue(), False, ""

    except Exception as e:
        sys.settrace(None)
        sys.stdout = sys.__stdout__

        tipo_error      = type(e).__name__
        mensaje_tecnico = str(e)
        mensaje_amigable = explicar_error(tipo_error + ": " + mensaje_tecnico)

        mensaje_final = (
            f"🔧 Tipo: {tipo_error}\n"
            f"📄 Detalle: {mensaje_tecnico}\n\n"
            f"🧠 Explicación:\n{mensaje_amigable}"
        )

        return salida_capturada.getvalue(), True, mensaje_final

    finally:
        sys.settrace(None)
        sys.stdout = sys.__stdout__
