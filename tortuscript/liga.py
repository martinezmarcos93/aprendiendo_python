"""
Liga semanal LOCAL. Compiten los perfiles de esta misma PC; si faltan para completar el grupo
se suman rivales simulados (siempre los mismos en la misma semana y liga). Sin internet, sin
cuentas y sin castigos: los 3 mejores del grupo suben de liga, el resto se queda donde está.

Todo es puro (recibe `hoy` y los datos de los otros perfiles) para poder probarlo.
"""
import random
import zlib
from datetime import timedelta

from . import progreso as _progreso

LIGAS = (("Bronce", "🥉"), ("Plata", "🥈"), ("Oro", "🥇"), ("Zafiro", "💎"), ("Rubí", "♦️"), ("Diamante", "👑"))
RIVALES = (("Nube", "☁️"), ("Pixel", "👾"), ("Luna", "🌙"), ("Cohete", "🚀"), ("Fénix", "🐦"),
           ("Tuerca", "🔩"), ("Zorro", "🦊"), ("Coral", "🪸"))
GRUPO = 5                      # participantes por grupo
ASCIENDEN = 3                  # puestos que suben de liga
XP_BASE = (120, 180, 260, 360, 480, 620)          # XP semanal típico de un rival en cada liga
AVANCE_DIARIO = (0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.0)   # cuánto del total lleva un rival cada día


def clave_semana(dia):
    anio, semana, _ = dia.isocalendar()
    return f"{anio}-W{semana:02d}"


def lunes_de(dia):
    return dia - timedelta(days=dia.weekday())


def xp_de_la_semana(xp_por_dia, dia):
    """XP de lunes a `dia` (inclusive) de la semana de `dia`."""
    lunes = lunes_de(dia)
    return sum(xp_por_dia.get(str(lunes + timedelta(days=i)), 0) for i in range((dia - lunes).days + 1))


def dias_restantes(hoy):
    """Días que faltan para que termine la semana (0 = hoy es domingo, último día)."""
    return 6 - hoy.weekday()


def rivales(semana, nivel, cantidad):
    """Rivales simulados, siempre los mismos para esa semana y liga: [{nombre, icono, total}]."""
    azar = random.Random(zlib.crc32(f"{semana}:{nivel}".encode("utf-8")))
    elegidos = azar.sample(RIVALES, min(cantidad, len(RIVALES)))
    base = XP_BASE[min(max(nivel, 0), len(XP_BASE) - 1)]
    salida = []
    for nombre, icono in elegidos:
        total = round(base * (0.55 + 0.9 * azar.random()))
        salida.append({"nombre": nombre, "icono": icono, "total": total})
    return salida


def xp_rival_hasta(rival, dia):
    """XP que lleva un rival simulado en `dia` (crece parejo a lo largo de la semana)."""
    return round(rival["total"] * AVANCE_DIARIO[dia.weekday()])


def tabla(nombre, xp_propio, otros_reales, nivel, dia):
    """La tabla del grupo en `dia`: mis XP, los de otros perfiles de la PC y rivales simulados.
    Devuelve filas ordenadas [{puesto, nombre, icono, xp, yo}]; en empate gana quien tiene nombre primero."""
    reales = sorted(otros_reales.items())[: GRUPO - 1]
    filas = [{"nombre": nombre, "icono": "🐢", "xp": xp_propio, "yo": True}]
    filas += [{"nombre": n, "icono": "🧒", "xp": x, "yo": False} for n, x in reales]
    for rival in rivales(clave_semana(dia), nivel, GRUPO - len(filas)):
        filas.append({"nombre": rival["nombre"], "icono": rival["icono"], "xp": xp_rival_hasta(rival, dia), "yo": False})
    filas.sort(key=lambda f: (-f["xp"], not f["yo"], f["nombre"]))
    for i, fila in enumerate(filas, 1):
        fila["puesto"] = i
    return filas


def resumen(progreso, otros_reales, hoy):
    """Todo lo que la página necesita: liga, tabla de la semana y días restantes."""
    nivel = progreso.get("liga", {}).get("nivel", 0)
    nombre = progreso.get("config", {}).get("nombre") or progreso.get("_perfil", "yo")
    xp = xp_de_la_semana(progreso.get("xp_por_dia", {}), hoy)
    filas = tabla(nombre, xp, otros_reales, nivel, hoy)
    yo = next(f for f in filas if f["yo"])
    return {"nivel": nivel, "liga": LIGAS[nivel][0], "icono": LIGAS[nivel][1], "filas": filas, "puesto": yo["puesto"],
            "xp": xp, "dias_restantes": dias_restantes(hoy), "asciende": yo["puesto"] <= ASCIENDEN and xp > 0,
            "ascienden": ASCIENDEN, "tamano": len(filas), "ultima": nivel >= len(LIGAS) - 1}


def cerrar_semana(progreso, xp_otros_de_la_semana, hoy):
    """Al empezar una semana nueva: resuelve la anterior (si el chico jugó y quedó entre los que
    suben, sube de liga) y deja anotada la semana actual. Devuelve el aviso o None. No guarda."""
    actual = clave_semana(hoy)
    liga = progreso.setdefault("liga", {"nivel": 0, "semana": None})
    if liga.get("semana") in (None, actual):
        liga["semana"] = actual
        return None
    domingo = lunes_de(hoy) - timedelta(days=1)            # último día de la semana que se cierra
    xp = xp_de_la_semana(progreso.get("xp_por_dia", {}), domingo)
    nivel = liga.get("nivel", 0)
    aviso = None
    if xp > 0:
        nombre = progreso.get("config", {}).get("nombre") or progreso.get("_perfil", "yo")
        filas = tabla(nombre, xp, xp_otros_de_la_semana(domingo), nivel, domingo)
        puesto = next(f["puesto"] for f in filas if f["yo"])
        if puesto <= ASCIENDEN and nivel < len(LIGAS) - 1:
            liga["nivel"] = nivel + 1
            aviso = {"tipo": "liga_asciende", "liga": LIGAS[nivel + 1][0], "icono": LIGAS[nivel + 1][1], "puesto": puesto}
            _progreso.avisar(progreso, **aviso)
    liga["semana"] = actual
    return aviso
