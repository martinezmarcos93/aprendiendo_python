"""Abre TortuScript en el navegador (versión web).

Uso:  .venv/bin/python iniciar_web.py        (o doble clic en el lanzador)
"""
import logging
import os
import socket
import sys
import threading
import webbrowser
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PUERTO_PREFERIDO = 5057


def _logs():
    carpeta = RAIZ / "logs"
    carpeta.mkdir(exist_ok=True)
    h = TimedRotatingFileHandler(carpeta / "tortuscript.log", when="midnight", backupCount=7, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    raiz = logging.getLogger("tortuscript")
    raiz.setLevel(logging.INFO)
    raiz.addHandler(h)


def _puerto_libre():
    for puerto in range(PUERTO_PREFERIDO, PUERTO_PREFERIDO + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", puerto)) != 0:
                return puerto
    raise RuntimeError("No encontré un puerto libre")


def main():
    _logs()
    sys.path.insert(0, str(RAIZ))
    from web.app import create_app
    app = create_app()
    puerto = _puerto_libre()
    url = f"http://127.0.0.1:{puerto}/"
    if "--sin-navegador" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"🐢 TortuScript está en {url}  (Ctrl+C para cerrar)")
    app.run(host="127.0.0.1", port=puerto, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    main()
