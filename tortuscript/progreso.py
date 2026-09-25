"""
Progreso del chico: XP, estrellas, racha, sesión del día y perfiles.

Guardado seguro:
- Escritura atómica (archivo temporal + os.replace): un corte a mitad nunca deja
  el JSON a medio escribir.
- Antes de reemplazar se guarda una copia `.bak` del progreso anterior.
- Si el JSON está dañado, NO se pisa: se aparta como `.corrupto-<fecha>` y se
  recupera desde el `.bak` (o se empieza de cero si no hay copia).
- Cada progreso cargado recuerda su perfil (`_perfil`), así una ventana abierta
  con el perfil A nunca guarda sobre el archivo del perfil B.
"""
import copy
import json
import logging
import os
import re
import shutil
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

logger = logging.getLogger("tortuscript.progreso")

# Los archivos viven en la carpeta raíz del proyecto (no en la carpeta desde donde se
# lo abre, ni dentro del paquete tortuscript/).
DIRECTORIO = Path(__file__).resolve().parent.parent
VERSION_ESQUEMA = 2

PERFIL_ACTUAL = "default"


# ─────────────────────────────────────────
# PERFILES
# ─────────────────────────────────────────
def sanitizar_perfil(nombre):
    """Minúsculas, solo letras/números/_/- (con tildes y ñ), máximo 30 caracteres."""
    nombre = (nombre or "").strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9ñáéíóúü_-]", "", nombre)[:30]


def set_perfil(nombre):
    global PERFIL_ACTUAL
    limpio = sanitizar_perfil(nombre)
    if limpio:
        PERFIL_ACTUAL = limpio
    return PERFIL_ACTUAL


def _archivo_config():
    return DIRECTORIO / "config_tortuscript.json"


def recordar_perfil(nombre):
    """Guarda cuál fue el último perfil usado, para abrir con ese la próxima vez."""
    try:
        _archivo_config().write_text(json.dumps({"ultimo_perfil": nombre}), encoding="utf-8")
    except OSError as e:
        logger.error("No se pudo recordar el perfil: %s", e, exc_info=True)


def perfil_recordado():
    try:
        nombre = json.loads(_archivo_config().read_text(encoding="utf-8")).get("ultimo_perfil")
    except (OSError, ValueError, AttributeError):
        return "default"
    return sanitizar_perfil(nombre) or "default"


def get_archivo_progreso(perfil=None):
    return DIRECTORIO / f"progreso_{perfil or PERFIL_ACTUAL}.json"


def obtener_perfiles():
    perfiles = {p.name[len("progreso_"):-len(".json")] for p in DIRECTORIO.glob("progreso_*.json")}
    perfiles.add("default")
    return sorted(perfiles)


PROGRESO_INICIAL = {
    "version": VERSION_ESQUEMA,
    "xp_total": 0,
    "ejercicios": {},
    "racha": 0,
    "racha_max": 0,
    "ultimo_dia": None,       # "YYYY-MM-DD"
    "dias_activo": [],        # lista de "YYYY-MM-DD" únicos, últimos 90
    "sesion_hoy": [],         # índices completados en `ultimo_dia`
}


# ─────────────────────────────────────────
# CARGA / GUARDADO
# ─────────────────────────────────────────
def _leer(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("ejercicios", {}), dict):
        raise ValueError("estructura de progreso inválida")
    return data


def _migrar(data):
    for campo, valor in PROGRESO_INICIAL.items():
        if campo not in data:
            data[campo] = copy.deepcopy(valor)
    data["version"] = VERSION_ESQUEMA
    return data


def cargar_progreso(perfil=None):
    perfil = perfil or PERFIL_ACTUAL
    archivo = get_archivo_progreso(perfil)
    data = None
    if archivo.exists():
        try:
            data = _leer(archivo)
        except (OSError, ValueError) as e:
            marca = datetime.now().strftime("%Y%m%d-%H%M%S")
            apartado = archivo.with_name(f"{archivo.name}.corrupto-{marca}")
            logger.error("Progreso dañado en %s: %s — se aparta como %s", archivo, e, apartado.name)
            try:
                os.replace(archivo, apartado)
            except OSError as e2:
                logger.error("No se pudo apartar el progreso dañado: %s", e2, exc_info=True)
            respaldo = archivo.with_name(archivo.name + ".bak")
            if respaldo.exists():
                try:
                    data = _leer(respaldo)
                    logger.warning("Progreso recuperado desde %s", respaldo.name)
                except (OSError, ValueError) as e3:
                    logger.error("El respaldo también está dañado: %s", e3)
    data = _migrar(data) if data is not None else copy.deepcopy(PROGRESO_INICIAL)
    data["_perfil"] = perfil
    return data


def guardar_progreso(progreso):
    """Guarda de forma atómica. Devuelve True si pudo guardar."""
    perfil = progreso.get("_perfil") or PERFIL_ACTUAL
    archivo = get_archivo_progreso(perfil)
    datos = {k: v for k, v in progreso.items() if not k.startswith("_")}
    tmp = None
    try:
        archivo.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".progreso_", suffix=".tmp", dir=str(archivo.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        if archivo.exists():
            shutil.copy2(archivo, archivo.with_name(archivo.name + ".bak"))
        os.replace(tmp, archivo)
        return True
    except OSError as e:
        logger.error("No se pudo guardar el progreso en %s: %s", archivo, e, exc_info=True)
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
        return False


# ─────────────────────────────────────────
# RACHA DIARIA
# ─────────────────────────────────────────
def actualizar_racha(progreso, hoy=None):
    """
    Llamar cuando el usuario completa un ejercicio.
    Retorna (racha_actual, es_dia_nuevo).
    """
    hoy = hoy or date.today()
    hoy_s = str(hoy)
    ultimo = progreso.get("ultimo_dia")

    if ultimo == hoy_s:
        return progreso.get("racha", 1), False

    if ultimo == str(hoy - timedelta(days=1)):
        progreso["racha"] = progreso.get("racha", 0) + 1
    else:
        progreso["racha"] = 1

    progreso["racha_max"] = max(progreso.get("racha_max", 0), progreso["racha"])
    progreso["ultimo_dia"] = hoy_s

    dias = progreso.get("dias_activo", [])
    if hoy_s not in dias:
        dias.append(hoy_s)
    progreso["dias_activo"] = dias[-90:]

    # Día nuevo → la sesión de hoy arranca vacía
    progreso["sesion_hoy"] = []
    return progreso["racha"], True


def racha_vigente(progreso, hoy=None):
    """La racha que corresponde mostrar: si el último día jugado fue antes de ayer,
    la racha ya se cortó (aunque el archivo todavía guarde el número viejo)."""
    hoy = hoy or date.today()
    ultimo = progreso.get("ultimo_dia")
    if ultimo in (str(hoy), str(hoy - timedelta(days=1))):
        return progreso.get("racha", 0)
    return 0


def registrar_sesion_hoy(progreso, indice):
    sesion = progreso.get("sesion_hoy", [])
    if indice not in sesion:
        sesion.append(indice)
    progreso["sesion_hoy"] = sesion


# ─────────────────────────────────────────
# REGISTRO DE EJERCICIO
# ─────────────────────────────────────────
def registrar_ejercicio(progreso, indice, estrellas, xp_ganado):
    """Registra un ejercicio RESUELTO. Solo suma XP si mejora el puntaje anterior."""
    key = str(indice)
    anterior = progreso["ejercicios"].get(key, {})
    hubo_mejora = estrellas > anterior.get("estrellas", 0)

    if hubo_mejora:
        progreso["xp_total"] = progreso.get("xp_total", 0) + xp_ganado - anterior.get("xp", 0)
        progreso["ejercicios"][key] = {"estrellas": estrellas, "xp": xp_ganado, "completado": True}

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


def resumen_sesion_hoy(progreso, ejercicios_lista, hoy=None):
    hoy = hoy or date.today()
    # `sesion_hoy` solo vale si el último día jugado es hoy
    indices_hoy = progreso.get("sesion_hoy", []) if progreso.get("ultimo_dia") == str(hoy) else []
    completados, xp_hoy, niveles_vistos = [], 0, set()

    for idx in indices_hoy:
        if idx < len(ejercicios_lista):
            ej = ejercicios_lista[idx]
            datos = progreso["ejercicios"].get(str(idx), {})
            completados.append({
                "titulo": ej["titulo"],
                "estrellas": datos.get("estrellas", 0),
                "xp": datos.get("xp", 0),
            })
            xp_hoy += datos.get("xp", 0)
            niveles_vistos.add(ej["nivel"])

    conceptos = [CONCEPTO_NIVEL[nv] for nv in sorted(niveles_vistos) if nv in CONCEPTO_NIVEL]
    return {"completados": completados, "xp_ganado_hoy": xp_hoy, "conceptos": conceptos}


def calendario_semana(progreso, hoy=None):
    """Los últimos 7 días (el más viejo primero) para el mini calendario del resumen."""
    hoy = hoy or date.today()
    activos = set(progreso.get("dias_activo", []))
    dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
    return [{"dia": d.day, "fecha": str(d), "activo": str(d) in activos, "hoy": d == hoy}
            for d in dias]


# ─────────────────────────────────────────
# NIVEL Y UTILIDADES
# ─────────────────────────────────────────
# Con 30 ejercicios a 30 XP el máximo es 900: el nivel 10 tiene que ser alcanzable.
UMBRALES_NIVEL = [0, 50, 110, 180, 260, 350, 450, 560, 680, 800]
_TRAMO_FINAL = 100


def calcular_nivel(xp):
    """Retorna (nivel, xp_en_nivel, xp_para_siguiente)."""
    nivel = 1
    for i, umbral in enumerate(UMBRALES_NIVEL):
        if xp >= umbral:
            nivel = i + 1
    base = UMBRALES_NIVEL[nivel - 1]
    if nivel < len(UMBRALES_NIVEL):
        return nivel, xp - base, UMBRALES_NIVEL[nivel] - base
    return nivel, min(xp - base, _TRAMO_FINAL), _TRAMO_FINAL


def estrellas_texto(n):
    return "⭐" * n + "☆" * (3 - n)


def titulo_nivel(nivel):
    titulos = {
        1: "🐣 Aprendiz",
        2: "🐢 Tortuga",
        3: "🐍 Serpiente",
        4: "🦎 Lagarto",
        5: "🦅 Águila",
        6: "🔥 Dragón",
        7: "💎 Cristal",
        8: "🚀 Cohete",
        9: "⚡ Rayo",
        10: "🏆 Maestro",
    }
    return titulos.get(nivel, "🏆 Maestro")
