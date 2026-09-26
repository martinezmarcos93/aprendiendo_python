"""
Exportar e importar el progreso de un perfil (para cambiar de compu o guardar una copia).

Todo es local: el archivo lo descarga y lo vuelve a subir el chico o un adulto; nada sale a internet.
Un archivo importado es una entrada de afuera: se valida campo por campo contra el esquema del progreso,
se descartan los campos desconocidos y nunca pisa un perfil existente (crea uno nuevo).
"""
import copy
import re
from datetime import date

from . import progreso, proyectos

FORMATO = "tortuscript-progreso"
VERSION_FORMATO = 1
MAX_BYTES = 1_000_000          # 30 proyectos de 5000 caracteres rondan 150 KB: sobra lugar


class ErrorImportacion(ValueError):
    """El archivo no se puede importar (el mensaje se le muestra al chico)."""


def exportar(datos_progreso, perfil):
    """El sobre que se descarga: identifica el formato y lleva el progreso sin campos internos."""
    limpio = {k: copy.deepcopy(v) for k, v in datos_progreso.items() if not k.startswith("_")}
    return {"formato": FORMATO, "version": VERSION_FORMATO, "perfil": perfil,
            "exportado": date.today().isoformat(), "progreso": limpio}


def nombre_de_archivo(perfil, hoy=None):
    return f"tortuscript-{perfil}-{(hoy or date.today()).isoformat()}.json"


def _tipo_valido(valor, modelo):
    if isinstance(modelo, bool):
        return isinstance(valor, bool)
    if isinstance(modelo, int):
        return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 0
    if modelo is None:                               # ultimo_dia: "YYYY-MM-DD" o null
        return valor is None or isinstance(valor, str)
    return isinstance(valor, type(modelo))


def validar(sobre):
    """Devuelve (progreso listo para guardar, nombre de perfil sugerido) o lanza ErrorImportacion."""
    if not isinstance(sobre, dict) or sobre.get("formato") != FORMATO:
        raise ErrorImportacion("Ese archivo no es un progreso de TortuScript.")
    if not isinstance(sobre.get("version"), int) or sobre["version"] > VERSION_FORMATO:
        raise ErrorImportacion("Ese archivo viene de una versión más nueva de TortuScript. Actualizá la app.")
    datos = sobre.get("progreso")
    if not isinstance(datos, dict):
        raise ErrorImportacion("Al archivo le falta el progreso.")
    version = datos.get("version", 1)
    if not isinstance(version, int) or isinstance(version, bool) or version > progreso.VERSION_ESQUEMA:
        raise ErrorImportacion("Ese progreso viene de una versión más nueva de TortuScript. Actualizá la app.")

    limpio = {}
    for campo, modelo in progreso.PROGRESO_INICIAL.items():
        if campo not in datos:
            continue                                  # _migrar lo completa (el esquema solo crece)
        if not _tipo_valido(datos[campo], modelo):
            raise ErrorImportacion(f"El archivo está dañado (el dato «{campo}» no es válido).")
        limpio[campo] = copy.deepcopy(datos[campo])
    config = limpio.get("config", {})
    for clave, modelo in progreso.PROGRESO_INICIAL["config"].items():
        if clave in config and not (config[clave] is None or _tipo_valido(config[clave], modelo)):
            raise ErrorImportacion(f"El archivo está dañado (el ajuste «{clave}» no es válido).")
    _validar_config(config)
    if "proyectos" in limpio:
        limpio["proyectos"] = _proyectos_validos(limpio["proyectos"])
    limpio = progreso._migrar(limpio)                 # mismo camino que un progreso viejo guardado en disco
    sugerido = progreso.sanitizar_perfil(str(sobre.get("perfil") or "")) or "importado"
    return limpio, sugerido


def _validar_config(config):
    """Las mismas reglas que al guardar la configuración desde la app."""
    if config.get("meta_min", progreso.METAS_MIN[0]) not in progreso.METAS_MIN:
        raise ErrorImportacion("El archivo está dañado (la meta diaria no es válida).")
    if config.get("experiencia") not in (None,) + progreso.EXPERIENCIAS:
        raise ErrorImportacion("El archivo está dañado (la experiencia no es válida).")
    if isinstance(config.get("nombre"), str):
        config["nombre"] = config["nombre"][:30]
    if "ajustes" in config:                           # los valores desconocidos se descartan (vuelven los de fábrica)
        config["ajustes"] = {k: v for k, v in config["ajustes"].items()
                             if v in progreso.AJUSTES.get(k, ())}


_ID_PROYECTO = re.compile(r"^[0-9a-f]{1,16}$")


def _proyectos_validos(lista):
    """Los proyectos cumplen las mismas reglas que al guardarlos desde Experimentar o la Zona Tortuga."""
    if len(lista) > proyectos.MAX_PROYECTOS:
        raise ErrorImportacion(f"El archivo tiene más de {proyectos.MAX_PROYECTOS} proyectos.")
    salida = {}
    for pid, p in lista.items():
        if not (_ID_PROYECTO.match(str(pid)) and isinstance(p, dict) and p.get("tipo") in proyectos.TIPOS
                and isinstance(p.get("codigo"), str) and len(p["codigo"]) <= proyectos.MAX_CODIGO
                and isinstance(p.get("nombre"), str) and p["nombre"].strip()):
            raise ErrorImportacion("El archivo está dañado (hay un proyecto que no es válido).")
        salida[pid] = {"nombre": p["nombre"].strip()[:proyectos.MAX_NOMBRE], "tipo": p["tipo"], "codigo": p["codigo"],
                       "creado": str(p.get("creado") or "")[:10], "actualizado": str(p.get("actualizado") or "")[:10]}
    return salida


def nombre_libre(base, existentes):
    """`base` si no existe; si no, base_2, base_3... (importar nunca pisa un perfil)."""
    if base not in existentes:
        return base
    n = 2
    while f"{base[:26]}_{n}" in existentes:
        n += 1
    return f"{base[:26]}_{n}"
