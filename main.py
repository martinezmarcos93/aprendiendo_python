import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Linux + IBus: cuando IBus atiende a las apps X por XIM (XMODIFIERS=@im=ibus) se
# traga el Intro del teclado numérico en las ventanas Tk (verificado: el evento
# KP_Enter nunca llega). Con el método de entrada propio de X (@im=none) el Intro
# numérico llega y las teclas muertas (´ + a = á) se siguen componiendo.
# Tiene que definirse ANTES de crear la ventana de Tk.
if sys.platform.startswith("linux") and "ibus" in os.environ.get("XMODIFIERS", ""):
    os.environ["XMODIFIERS"] = "@im=none"

from ui.main_window import SistemaPrincipal  # noqa: E402  (después de ajustar el entorno)


def _configurar_logs():
    """Errores internos a logs/tortuscript.log (rotación diaria, 7 días).
    Al chico nunca se le muestra esto: es para depurar."""
    carpeta = Path(__file__).resolve().parent / "logs"
    try:
        carpeta.mkdir(exist_ok=True)
        handler = TimedRotatingFileHandler(carpeta / "tortuscript.log", when="midnight",
                                           backupCount=7, encoding="utf-8")
    except OSError:
        return
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    raiz = logging.getLogger("tortuscript")
    raiz.setLevel(logging.INFO)
    raiz.addHandler(handler)


if __name__ == "__main__":
    _configurar_logs()
    app = SistemaPrincipal()
    app.mainloop()
