"""
Práctica del día: repaso espaciado (cajas de Leitner) e intercalado (se mezclan lecciones).

Cada paso rápido de una lección terminada (elegir, predecir, completar, ordenar) es una "tarjeta"
que se vuelve a ver cada vez más espaciada mientras se responda bien al primer intento:
caja 0 (nuevo) → 1 → 2 → 3 → 4 → 5, con INTERVALOS de días entre repasos. Un error la manda de
vuelta a la caja 1 (mañana). Sin castigos: solo se reprograma.

Todo es puro: recibe `hoy` y los cursos, no toca disco.
"""
from datetime import date, timedelta

INTERVALOS = (1, 2, 4, 8, 16)          # días de espera al pasar a la caja 1..5
MAX_CAJA = len(INTERVALOS)
TIPOS = ("elegir", "predecir", "completar", "ordenar")
POR_SESION = 6
MAX_POR_LECCION = 2
XP_ACIERTO = 2                          # XP por acertar al primer intento en la práctica
XP_MAXIMO_DIARIO = 12


def clave(leccion_id, paso):
    return f"{leccion_id}:{paso}"


def _vencimiento(progreso, leccion_id, paso, registro_paso):
    """Fecha en que la tarjeta toca: la programada o, si es nueva, un día después de haberla terminado."""
    guardado = (progreso.get("repaso") or {}).get(clave(leccion_id, paso))
    if guardado and guardado.get("proximo"):
        return date.fromisoformat(guardado["proximo"])
    fecha = registro_paso.get("fecha")
    return date.fromisoformat(fecha) + timedelta(days=1) if fecha else date.min     # sin fecha (progreso viejo): ya toca


def candidatos(progreso, cursos, hoy):
    """Tarjetas que ya tocan, de las lecciones donde hay pasos terminados:
    [{leccion, paso, vencido, caja}] (vencido = días de atraso)."""
    por_id = {lec["id"]: lec for curso in cursos for seccion in curso["secciones"] for lec in seccion["lecciones"]}
    salida = []
    for leccion_id, datos in (progreso.get("lecciones") or {}).items():
        lec = por_id.get(leccion_id)
        if lec is None:
            continue
        for indice_s, registro in (datos.get("pasos") or {}).items():
            indice = int(indice_s)
            if indice >= len(lec["pasos"]) or lec["pasos"][indice]["tipo"] not in TIPOS:
                continue
            vence = _vencimiento(progreso, leccion_id, indice, registro)
            if vence <= hoy:
                caja = ((progreso.get("repaso") or {}).get(clave(leccion_id, indice)) or {}).get("caja", 0)
                salida.append({"leccion": leccion_id, "paso": indice, "vencido": (hoy - vence).days if vence > date.min else 9999,
                               "caja": caja})
    return salida


def pendientes(progreso, cursos, hoy):
    return len(candidatos(progreso, cursos, hoy))


def elegir(progreso, cursos, hoy, cantidad=POR_SESION):
    """La sesión de hoy: lo más atrasado primero e INTERCALANDO lecciones (a lo sumo 2 por lección),
    así no se practica siempre lo mismo seguido. Devuelve [(leccion_id, paso)]."""
    grupos = {}
    for c in candidatos(progreso, cursos, hoy):
        grupos.setdefault(c["leccion"], []).append(c)
    for lista in grupos.values():
        lista.sort(key=lambda c: (-c["vencido"], c["caja"], c["paso"]))
    orden = sorted(grupos, key=lambda l: (-grupos[l][0]["vencido"], l))            # primero la lección más atrasada
    elegidas, ronda = [], 0
    limite = max(MAX_POR_LECCION, -(-cantidad // max(1, len(orden))))        # con pocas lecciones, algo más por lección
    while len(elegidas) < cantidad and ronda < limite:
        for leccion_id in orden:
            if len(grupos[leccion_id]) > ronda and len(elegidas) < cantidad:
                elegidas.append((leccion_id, grupos[leccion_id][ronda]["paso"]))
        ronda += 1
    return elegidas


def registrar(progreso, leccion_id, paso, acierto, hoy):
    """Reprograma la tarjeta. Acierto al primer intento: sube de caja; si no, vuelve a la caja 1 (mañana)."""
    tarjetas = progreso.setdefault("repaso", {})
    t = tarjetas.setdefault(clave(leccion_id, paso), {"caja": 0, "aciertos": 0, "fallos": 0})
    if acierto:
        t["caja"] = min(t["caja"] + 1, MAX_CAJA)
        t["aciertos"] += 1
    else:
        t["caja"] = 1
        t["fallos"] += 1
    t["proximo"] = str(hoy + timedelta(days=INTERVALOS[t["caja"] - 1]))
    return t
