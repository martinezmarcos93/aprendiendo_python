"""
Mis proyectos: guardar, abrir, duplicar y borrar lo que se hace en Experimentar y en la Zona
Tortuga. Se guardan dentro del progreso del perfil (progreso["proyectos"]), así viajan con él
y no hay nada más que administrar.

Todo es puro (no toca disco): recibe el dict de progreso y quien llama guarda.
"""
import re
import secrets
from datetime import date

TIPOS = ("experimentar", "tortuga")
MAX_PROYECTOS = 30
MAX_CODIGO = 5000
MAX_NOMBRE = 40


class ErrorProyecto(ValueError):
    """Algo que el chico puede corregir; el mensaje se le muestra tal cual."""


def _nombre_limpio(nombre):
    limpio = re.sub(r"\s+", " ", str(nombre or "")).strip()
    if not limpio:
        raise ErrorProyecto("Ponele un nombre a tu proyecto.")
    return limpio[:MAX_NOMBRE]


def guardar(progreso, nombre, tipo, codigo, proyecto_id=None, hoy=None):
    """Crea un proyecto o, si se pasa `proyecto_id` de uno existente, lo actualiza. Devuelve su id."""
    if tipo not in TIPOS:
        raise ErrorProyecto("Ese tipo de proyecto no existe.")
    codigo = str(codigo or "")
    if len(codigo) > MAX_CODIGO:
        raise ErrorProyecto(f"Tu proyecto es muy largo (máximo {MAX_CODIGO} letras).")
    nombre = _nombre_limpio(nombre)
    proyectos = progreso.setdefault("proyectos", {})
    hoy_s = str(hoy or date.today())
    if proyecto_id in proyectos:
        p = proyectos[proyecto_id]
        p.update(nombre=nombre, codigo=codigo, actualizado=hoy_s)
        return proyecto_id
    if len(proyectos) >= MAX_PROYECTOS:
        raise ErrorProyecto(f"Ya tenés {MAX_PROYECTOS} proyectos: borrá alguno para guardar uno nuevo.")
    nuevo = secrets.token_hex(4)
    while nuevo in proyectos:
        nuevo = secrets.token_hex(4)
    proyectos[nuevo] = {"nombre": nombre, "tipo": tipo, "codigo": codigo, "creado": hoy_s, "actualizado": hoy_s}
    return nuevo


def obtener(progreso, proyecto_id):
    p = (progreso.get("proyectos") or {}).get(proyecto_id)
    return None if p is None else {"id": proyecto_id, **p}


def duplicar(progreso, proyecto_id, hoy=None):
    original = obtener(progreso, proyecto_id)
    if original is None:
        raise ErrorProyecto("Ese proyecto no existe.")
    nombre = f"Copia de {original['nombre']}"[:MAX_NOMBRE]
    return guardar(progreso, nombre, original["tipo"], original["codigo"], hoy=hoy)


def borrar(progreso, proyecto_id):
    if proyecto_id not in (progreso.get("proyectos") or {}):
        raise ErrorProyecto("Ese proyecto no existe.")
    del progreso["proyectos"][proyecto_id]


def listar(progreso):
    """Los más recientes primero (empate: por nombre)."""
    todos = [{"id": i, **p} for i, p in (progreso.get("proyectos") or {}).items()]
    return sorted(todos, key=lambda p: (p["actualizado"], p["creado"]), reverse=True) if todos else []
