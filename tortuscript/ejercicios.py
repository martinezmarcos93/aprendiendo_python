"""Compatibilidad: los ejercicios ahora viven en contenido/cursos/primeros-pasos.json.

EJERCICIOS es la vista "un ejercicio por paso escribir" que usa la web (páginas /ejercicios/N,
Mapa y Repaso); sus índices son la clave histórica del progreso. Para editar el contenido, editá el
JSON y corré:  python3 herramientas/validar_contenido.py
"""
from .contenido import ejercicios

EJERCICIOS = ejercicios()
