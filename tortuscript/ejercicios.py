"""Compatibilidad: los ejercicios ahora viven en contenido/cursos/primeros-pasos.json.

EJERCICIOS es la vista "un ejercicio por paso escribir" que usan la app Tk y la web
mientras llega el motor de lecciones (Fase 1). Para editar el contenido, editá el
JSON y corré:  python3 herramientas/validar_contenido.py
"""
from .contenido import ejercicios

EJERCICIOS = ejercicios()
