"""
Logros: cosas que se ganan jugando. Solo se celebran: no hay logros que se pierdan ni que
comparen al chico con otros. La lista es de datos (LOGROS) y las condiciones son funciones puras
sobre un `resumen` del avance, así se prueban sin abrir la app.

resumen = {
  "pasos_hechos": int,               pasos de lección + ejercicios ya resueltos
  "hechas_ids": set[str],            lecciones completadas (de todos los cursos)
  "perfectas": int,                  lecciones perfectas
  "cursos": {curso_id: (hechas, total)},
  "estrellas3": int,                 ejercicios 'escribir' resueltos con 3 estrellas (sin pistas)
  "nivel": int,
  "proyectos": int,                  proyectos guardados
}
"""
from datetime import date

from . import progreso as _progreso

CURSO_1, CURSO_TORTUGA, CURSO_PYTHON = "primeros-pasos", "tortuga", "python-real"


def _curso_completo(curso_id):
    return lambda p, r: r["cursos"].get(curso_id, (0, 1))[0] >= r["cursos"].get(curso_id, (0, 1))[1] > 0


def _hechas(n):
    return lambda p, r: len(r["hechas_ids"]) >= n


def _racha(n):
    return lambda p, r: p.get("racha_max", 0) >= n


# (id, icono, título, descripción, condición(progreso, resumen))
LOGROS = (
    ("primer-paso", "👣", "Primer paso", "Completaste tu primer paso.", lambda p, r: r["pasos_hechos"] >= 1),
    ("primera-leccion", "🌱", "Primera lección", "Terminaste una lección entera.", _hechas(1)),
    ("cinco-lecciones", "🌿", "Cinco lecciones", "Ya terminaste 5 lecciones.", _hechas(5)),
    ("diez-lecciones", "🌳", "Diez lecciones", "Ya terminaste 10 lecciones.", _hechas(10)),
    ("veinticinco-lecciones", "🏔️", "25 lecciones", "¡25 lecciones terminadas!", _hechas(25)),
    ("perfecta", "⭐", "Lección perfecta", "Una lección entera sin errores ni ayudas.", lambda p, r: r["perfectas"] >= 1),
    ("cinco-perfectas", "🌟", "Cinco perfectas", "Cinco lecciones perfectas.", lambda p, r: r["perfectas"] >= 5),
    ("sin-pistas", "🧠", "Sin ayuda", "10 ejercicios resueltos con 3 estrellas.", lambda p, r: r["estrellas3"] >= 10),
    ("racha-3", "🔥", "Tres días seguidos", "Programaste 3 días seguidos.", _racha(3)),
    ("racha-7", "📅", "Una semana entera", "Cumpliste el reto de 7 días seguidos.", _racha(7)),
    ("racha-30", "🏅", "Un mes seguido", "¡30 días seguidos programando!", _racha(30)),
    ("primer-proyecto", "💾", "Primer proyecto", "Guardaste tu primer proyecto.", lambda p, r: r["proyectos"] >= 1),
    ("cinco-proyectos", "🗂️", "Cinco proyectos", "Ya tenés 5 proyectos guardados.", lambda p, r: r["proyectos"] >= 5),
    ("congelador", "❄️", "Congelador ganado", "Ganaste tu primer congelador de racha.",
     lambda p, r: p.get("stats", {}).get("congeladores_ganados", 0) >= 1),
    ("meta-diaria", "🎯", "Meta cumplida", "Llegaste a tu meta diaria.", lambda p, r: len(p.get("dias_meta", [])) >= 1),
    ("cinco-metas", "🎖️", "Cinco metas", "Cumpliste tu meta diaria 5 días.", lambda p, r: len(p.get("dias_meta", [])) >= 5),
    ("curso-1", "🏆", "Maestro de TortuScript", "Terminaste el curso Primeros pasos.", _curso_completo(CURSO_1)),
    ("primer-dibujo", "🎨", "Primer dibujo", "Terminaste la primera lección de la tortuga.",
     lambda p, r: "tortuga-avanzar" in r["hechas_ids"]),
    ("artista", "🖼️", "Artista", "Terminaste el curso de la tortuga.", _curso_completo(CURSO_TORTUGA)),
    ("primer-python", "🐍", "Primer Python", "Escribiste tu primer programa en Python.", lambda p, r: "py-print" in r["hechas_ids"]),
    ("programador", "💻", "Programador de Python", "Terminaste el puente a Python real.", _curso_completo(CURSO_PYTHON)),
    ("nivel-5", "🦅", "Nivel 5", "Llegaste al nivel 5.", lambda p, r: r["nivel"] >= 5),
    ("nivel-10", "👑", "Nivel 10", "¡Llegaste al nivel máximo!", lambda p, r: r["nivel"] >= 10),
    ("liga-plata", "🥈", "Liga de Plata", "Subiste a la liga de Plata.", lambda p, r: p.get("liga", {}).get("nivel", 0) >= 1),
    ("liga-oro", "🥇", "Liga de Oro", "Subiste a la liga de Oro.", lambda p, r: p.get("liga", {}).get("nivel", 0) >= 2),
)
IDS = tuple(l[0] for l in LOGROS)


def resumen_de(progreso, camino):
    """Arma el `resumen` a partir del progreso y del estado del camino (leccion.estado_cursos)."""
    hechas, perfectas, cursos = set(), 0, {}
    for curso in camino:
        h = t = 0
        for seccion in curso["secciones"]:
            for lec in seccion["lecciones"]:
                t += 1
                if lec["estado"] in ("hecha", "perfecta"):
                    h += 1
                    hechas.add(lec["id"])
                if lec["estado"] == "perfecta":
                    perfectas += 1
        cursos[curso["id"]] = (h, t)
    lecciones = progreso.get("lecciones", {})
    ejercicios = progreso.get("ejercicios", {})
    pasos = sum(len(l.get("pasos", {})) for l in lecciones.values()) + \
        sum(1 for e in ejercicios.values() if e.get("completado"))
    tres = sum(1 for e in ejercicios.values() if e.get("estrellas", 0) == 3) + \
        sum(1 for l in lecciones.values() for paso in l.get("pasos", {}).values()
            if paso.get("estrellas", 0) == 3 and paso.get("xp", 0) > 0)   # 'escribir' de cursos sin ejercicio clásico
    return {"pasos_hechos": pasos, "hechas_ids": hechas, "perfectas": perfectas, "cursos": cursos,
            "estrellas3": tres, "nivel": _progreso.calcular_nivel(progreso.get("xp_total", 0))[0],
            "proyectos": len(progreso.get("proyectos") or {})}


def cumplidos(progreso, resumen):
    return [id_ for id_, _, _, _, condicion in LOGROS if condicion(progreso, resumen)]


def revisar(progreso, resumen, hoy=None):
    """Anota (con fecha) los logros que recién se cumplen y deja el aviso. Devuelve sus ids.
    No guarda: lo hace quien llama junto con el resto del progreso."""
    hoy_s = str(hoy or date.today())
    ganados = progreso.setdefault("logros", {})
    nuevos = []
    for id_, icono, titulo, descripcion, condicion in LOGROS:
        if id_ not in ganados and condicion(progreso, resumen):
            ganados[id_] = hoy_s
            _progreso.avisar(progreso, "logro", id=id_, icono=icono, titulo=titulo, descripcion=descripcion)
            nuevos.append(id_)
    return nuevos


def catalogo(progreso):
    """Todos los logros con su estado, para la página de logros."""
    ganados = progreso.get("logros", {})
    return [{"id": id_, "icono": icono, "titulo": titulo, "descripcion": descripcion,
             "ganado": id_ in ganados, "fecha": ganados.get(id_)}
            for id_, icono, titulo, descripcion, _ in LOGROS]
