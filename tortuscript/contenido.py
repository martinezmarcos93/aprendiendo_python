"""
Contenido de los cursos como DATOS (contenido/cursos/*.json), no como código.

Estructura de un curso:

    {
      "id": "primeros-pasos", "titulo": "...", "version": 1,
      "secciones": [
        {"id": "mostrar", "nivel": 1, "titulo": "Mostrar",
         "lecciones": [
           {"id": "hola-mundo", "titulo": "1. Hola mundo",
            "pasos": [ {"tipo": "...", ...}, ... ]}
         ]}
      ]
    }

Tipos de paso (los 6 del roadmap "Mimo para chicos"):

  explicacion  {texto, codigo?}                      — leer (y ejecutar el ejemplo)
  elegir       {pregunta, codigo?, opciones[], correcta}  — tocar la opción correcta
  completar    {consigna, codigo (con ___), fichas[], respuesta[]}  — llenar huecos con fichas
  ordenar      {consigna, lineas[] (en orden correcto)}   — armar el programa
  predecir     {codigo, opciones[], correcta}         — ¿qué va a mostrar?
  escribir     {consigna, forma?, nota?, solucion, entradas_prueba?}  — programar

`forma` es la sintaxis que se presenta por primera vez (se muestra aparte);
`entradas_prueba` son respuestas para preguntar() al validar.
"""
import json
from functools import lru_cache
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent / "contenido" / "cursos"
CURSO_PRINCIPAL = "primeros-pasos"

TIPOS = ("explicacion", "elegir", "completar", "ordenar", "predecir", "escribir")
HUECO = "___"


@lru_cache(maxsize=None)
def cargar_curso(curso_id=CURSO_PRINCIPAL):
    with open(CARPETA / f"{curso_id}.json", encoding="utf-8") as f:
        return json.load(f)


def lecciones(curso):
    """Lista plana de (seccion, leccion) en el orden del curso."""
    return [(s, l) for s in curso["secciones"] for l in s["lecciones"]]


def pasos(curso):
    """Lista plana de (seccion, leccion, indice_paso, paso) en orden."""
    return [(s, l, i, p) for s, l in lecciones(curso) for i, p in enumerate(l["pasos"])]


def descripcion_completa(paso):
    """Consigna + forma + nota en una sola línea (para la app Tk y compatibilidad)."""
    texto = paso.get("consigna", "")
    if paso.get("forma"):
        texto += f'   Forma:  {paso["forma"]}'
    if paso.get("nota"):
        nota = paso["nota"]
        if not paso.get("forma"):
            texto += f" {nota}"
        else:
            texto += f"   {nota}" if nota.startswith("(") else f". {nota}"
    return texto


def ejercicios(curso_id=CURSO_PRINCIPAL):
    """Vista de compatibilidad: un ejercicio por cada paso 'escribir', en orden.

    El índice de esta lista es la clave del progreso guardado ("0".."29"), así que
    el orden de los pasos 'escribir' no debe cambiar sin migrar el progreso.
    """
    curso = cargar_curso(curso_id)
    salida = []
    for seccion, leccion, indice_paso, paso in pasos(curso):
        if paso["tipo"] != "escribir":
            continue
        salida.append({
            "nivel": seccion["nivel"],
            "titulo": leccion["titulo"],
            "descripcion": descripcion_completa(paso),
            "consigna": paso.get("consigna", ""),
            "forma": paso.get("forma"),
            "nota": paso.get("nota"),
            "solucion": paso["solucion"],
            "leccion_id": leccion["id"],
            "paso": indice_paso,
        })
    return salida


def indices_ejercicio(leccion_id, curso_id=CURSO_PRINCIPAL):
    """{índice_de_paso: índice_de_ejercicio} de los pasos 'escribir' de una lección."""
    return {e["paso"]: i for i, e in enumerate(ejercicios(curso_id)) if e["leccion_id"] == leccion_id}
