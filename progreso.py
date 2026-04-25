import json
import os
from datetime import date, timedelta

ARCHIVO_PROGRESO = "progreso_tortuscript.json"

PROGRESO_INICIAL = {
    "xp_total": 0,
    "ejercicios": {},
    "racha": 0,
    "racha_max": 0,
    "ultimo_dia": None,       # "YYYY-MM-DD"
    "dias_activo": [],        # lista de "YYYY-MM-DD" únicos, últimos 90
    "sesion_hoy": [],         # índices completados hoy (se limpia al día siguiente)
}

# ─────────────────────────────────────────
# CARGA / GUARDADO
# ─────────────────────────────────────────

def cargar_progreso():
    if os.path.exists(ARCHIVO_PROGRESO):
        try:
            with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
                data = json.load(f)
            # migrar archivos viejos que no tenían estos campos
            for campo, valor in PROGRESO_INICIAL.items():
                if campo not in data:
                    import copy
                    data[campo] = copy.deepcopy(valor)
            return data
        except Exception:
            pass
    import copy
    return copy.deepcopy(PROGRESO_INICIAL)


def guardar_progreso(progreso):
    try:
        with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
            json.dump(progreso, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ─────────────────────────────────────────
# RACHA DIARIA
# ─────────────────────────────────────────

def actualizar_racha(progreso):
    """
    Llama esto cuando el usuario completa un ejercicio.
    Retorna (racha_actual, es_dia_nuevo).
    es_dia_nuevo=True indica que hoy es la primera vez que juega
    (útil para mostrar animación de racha).
    """
    hoy = str(date.today())
    ultimo = progreso.get("ultimo_dia")

    if ultimo == hoy:
        return progreso.get("racha", 1), False

    ayer = str(date.today() - timedelta(days=1))

    if ultimo == ayer:
        progreso["racha"] = progreso.get("racha", 0) + 1
    else:
        progreso["racha"] = 1

    progreso["racha_max"] = max(
        progreso.get("racha_max", 0),
        progreso["racha"]
    )
    progreso["ultimo_dia"] = hoy

    dias = progreso.get("dias_activo", [])
    if hoy not in dias:
        dias.append(hoy)
    progreso["dias_activo"] = dias[-90:]

    # Nueva sesión → limpiar registro del día anterior
    progreso["sesion_hoy"] = []

    return progreso["racha"], True


def registrar_sesion_hoy(progreso, indice):
    sesion = progreso.get("sesion_hoy", [])
    if indice not in sesion:
        sesion.append(indice)
    progreso["sesion_hoy"] = sesion


# ─────────────────────────────────────────
# REGISTRO DE EJERCICIO
# ─────────────────────────────────────────

def registrar_ejercicio(progreso, indice, estrellas, xp_ganado):
    """Registra resultado. Solo actualiza XP si mejora el puntaje anterior."""
    key = str(indice)
    anterior = progreso["ejercicios"].get(key, {})
    estrellas_anterior = anterior.get("estrellas", 0)

    hubo_mejora = estrellas > estrellas_anterior

    if hubo_mejora:
        diff_xp = xp_ganado - anterior.get("xp", 0)
        progreso["xp_total"] = progreso.get("xp_total", 0) + diff_xp
        progreso["ejercicios"][key] = {
            "estrellas": estrellas,
            "xp": xp_ganado,
            "completado": True
        }

    # Racha y sesión se actualizan en cualquier intento exitoso
    if estrellas >= 1:
        actualizar_racha(progreso)
        registrar_sesion_hoy(progreso, indice)

    guardar_progreso(progreso)
    return hubo_mejora


# ─────────────────────────────────────────
# RESUMEN DE SESIÓN DE HOY
# ─────────────────────────────────────────

CONCEPTO_NIVEL = {
    1: "Mostrar texto",
    2: "Variables",
    3: "Entrada de datos",
    4: "Operaciones matemáticas",
    5: "Condicionales (si/sino)",
    6: "Bucles (repetir)",
    7: "Funciones",
    8: "Desafíos combinados",
}


def resumen_sesion_hoy(progreso, ejercicios_lista):
    """
    Retorna:
    {
      "completados": [{"titulo", "estrellas", "xp"}, ...],
      "xp_ganado_hoy": int,
      "conceptos": [str, ...]
    }
    """
    indices_hoy = progreso.get("sesion_hoy", [])
    completados = []
    xp_hoy = 0
    niveles_vistos = set()

    for idx in indices_hoy:
        if idx < len(ejercicios_lista):
            ej = ejercicios_lista[idx]
            datos = progreso["ejercicios"].get(str(idx), {})
            estrellas = datos.get("estrellas", 0)
            xp = datos.get("xp", 0)
            completados.append({
                "titulo":    ej["titulo"],
                "estrellas": estrellas,
                "xp":        xp,
            })
            xp_hoy += xp
            niveles_vistos.add(ej["nivel"])

    conceptos = [
        CONCEPTO_NIVEL[nv]
        for nv in sorted(niveles_vistos)
        if nv in CONCEPTO_NIVEL
    ]

    return {
        "completados":    completados,
        "xp_ganado_hoy":  xp_hoy,
        "conceptos":      conceptos,
    }


# ─────────────────────────────────────────
# NIVEL Y UTILIDADES
# ─────────────────────────────────────────

def calcular_nivel(xp):
    """Retorna (nivel, xp_en_nivel, xp_para_siguiente)"""
    thresholds = [0, 50, 120, 220, 350, 500, 700, 950, 1250, 1600, 2000]
    nivel = 1
    for i, umbral in enumerate(thresholds):
        if xp >= umbral:
            nivel = i + 1
        else:
            break
    nivel = min(nivel, len(thresholds))
    xp_base = thresholds[nivel - 1]
    xp_sig = thresholds[nivel] if nivel < len(thresholds) else thresholds[-1] + 500
    return nivel, xp - xp_base, xp_sig - xp_base


def estrellas_texto(n):
    return "⭐" * n + "☆" * (3 - n)


def titulo_nivel(nivel):
    titulos = {
        1:  "🐣 Aprendiz",
        2:  "🐢 Tortuga",
        3:  "🐍 Serpiente",
        4:  "🦎 Lagarto",
        5:  "🦅 Águila",
        6:  "🔥 Dragón",
        7:  "💎 Cristal",
        8:  "🚀 Cohete",
        9:  "⚡ Rayo",
        10: "🏆 Maestro",
    }
    return titulos.get(nivel, "🏆 Leyenda")
