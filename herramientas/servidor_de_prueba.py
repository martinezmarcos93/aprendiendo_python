#!/usr/bin/env python3
"""Servidor de PRUEBA: la app web con un progreso temporal (no toca los progreso_<perfil>.json reales).

Lo usan jugar_cursos.py y revisar_contraste.py, que manejan el navegador con Playwright (opcional:
pip install playwright && playwright install chromium; no está en requirements.txt).

Uso:  python herramientas/servidor_de_prueba.py [puerto] [--todo-desbloqueado] [--abrir]
      (puerto 5077 por defecto; --todo-desbloqueado deja todas las lecciones y ejercicios abiertos;
       --abrir abre el navegador; Ctrl+C para cortar)
"""
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tortuscript import progreso  # noqa: E402

TOKEN = "prueba"


def desbloquear_todo():
    """Marca todas las lecciones y ejercicios como abiertos (sin XP) en el progreso temporal."""
    from tortuscript import contenido
    p = progreso.cargar_progreso()
    progreso.guardar_config(p, onboarding=True, nombre="Prueba")
    for curso in contenido.todos_los_cursos():
        for _, lec in contenido.lecciones(curso):
            p.setdefault("lecciones", {})[lec["id"]] = {"pasos": {}, "completada": True, "perfecta": False}
    for i in range(len(contenido.ejercicios())):
        p["ejercicios"][str(i)] = {"completado": True, "estrellas": 1, "xp": 0}
    progreso.guardar_progreso(p)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    puerto = int(args[0]) if args else 5077
    progreso.DIRECTORIO = Path(tempfile.mkdtemp(prefix="tortu_prueba_"))
    if "--todo-desbloqueado" in sys.argv:
        desbloquear_todo()
    from iniciar_web import crear_servidor
    from web.app import create_app
    print(f"Servidor de prueba en http://127.0.0.1:{puerto} (progreso temporal en {progreso.DIRECTORIO})")
    if "--abrir" in sys.argv:
        import threading
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{puerto}/")).start()
    crear_servidor(puerto, create_app(token=TOKEN)).serve_forever()


if __name__ == "__main__":
    main()
