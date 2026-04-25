import sys
import io
from error_handler import explicar_error


# -------------------------
# INPUT SIMULADO
# Evita que input() congele la app.
# Devuelve "" y avisa al usuario.
# -------------------------
class InputSimulado:
    def __init__(self, salida_buffer):
        self._buf = salida_buffer
        self._usado = False

    def __call__(self, prompt=""):
        if prompt:
            self._buf.write(str(prompt))
        if not self._usado:
            self._usado = True
            self._buf.write(
                "\n⚠️  preguntar() no funciona en el modo ejercicios.\n"
                "   Probá la zona de Experimentar para usar entrada de datos.\n"
            )
        return ""


# -------------------------
# ENTORNO SEGURO
# Se crea fresco en cada ejecución para
# evitar que variables de una corrida
# contaminen la siguiente.
# -------------------------
def _hacer_globals(salida_buffer):
    input_sim = InputSimulado(salida_buffer)
    return {
        "__builtins__": {
            "print":  print,
            "input":  input_sim,
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
        exec(codigo_python, entorno)

        sys.stdout = sys.__stdout__
        return salida_capturada.getvalue(), False, ""

    except Exception as e:
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
        sys.stdout = sys.__stdout__
