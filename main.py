import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from ui.main_window import SistemaPrincipal


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
