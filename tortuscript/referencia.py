"""Guía del lenguaje (contenido/referencia.json). Cada ejemplo trae TortuScript y su Python."""
import json
from functools import lru_cache
from pathlib import Path

ARCHIVO = Path(__file__).resolve().parent.parent / "contenido" / "referencia.json"


@lru_cache(maxsize=None)
def cargar_referencia():
    with open(ARCHIVO, encoding="utf-8") as f:
        return json.load(f)
