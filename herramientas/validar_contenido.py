#!/usr/bin/env python3
"""Valida todos los cursos de contenido/cursos/ sin abrir la app.

Uso:  python3 herramientas/validar_contenido.py          (todos los cursos)
      python3 herramientas/validar_contenido.py primeros-pasos

Sale con código 1 si hay errores (❌). Los avisos (⚠️) son para revisar a mano.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortuscript.contenido import CARPETA, cargar_curso, pasos  # noqa: E402
from tortuscript.validacion import ERROR, validar_curso  # noqa: E402


def main():
    ids = sys.argv[1:] or sorted(p.stem for p in CARPETA.glob("*.json"))
    total_errores = 0
    for curso_id in ids:
        curso = cargar_curso(curso_id)
        hallazgos = validar_curso(curso)
        errores = [h for h in hallazgos if h.nivel == ERROR]
        avisos = [h for h in hallazgos if h.nivel != ERROR]
        total_errores += len(errores)
        n_pasos = len(pasos(curso))
        print(f"\n📚 {curso['titulo']} ({curso_id}) — {n_pasos} pasos revisados")
        for h in errores + avisos:
            print("   ", h)
        estado = "✅ sin errores" if not errores else f"❌ {len(errores)} error(es)"
        print(f"   {estado}, {len(avisos)} aviso(s)")
    sys.exit(1 if total_errores else 0)


if __name__ == "__main__":
    main()
