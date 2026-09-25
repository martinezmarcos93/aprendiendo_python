#!/usr/bin/env python3
"""Servidor de PRUEBA: la app web con un progreso temporal (no toca los progreso_<perfil>.json reales).

Lo usan jugar_cursos.py y revisar_contraste.py, que manejan el navegador con Playwright (opcional:
pip install playwright && playwright install chromium; no está en requirements.txt).

Uso:  python herramientas/servidor_de_prueba.py [puerto]      (por defecto 5077; Ctrl+C para cortar)
"""
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tortuscript import progreso  # noqa: E402

TOKEN = "prueba"


def main():
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 5077
    progreso.DIRECTORIO = Path(tempfile.mkdtemp(prefix="tortu_prueba_"))
    from iniciar_web import crear_servidor
    from web.app import create_app
    print(f"Servidor de prueba en http://127.0.0.1:{puerto} (progreso temporal en {progreso.DIRECTORIO})")
    crear_servidor(puerto, create_app(token=TOKEN)).serve_forever()


if __name__ == "__main__":
    main()
