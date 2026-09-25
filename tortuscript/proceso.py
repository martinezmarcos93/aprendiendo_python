"""
Corre el código del chico en un proceso aparte (tortuscript.worker), con límites:
tiempo real, CPU y memoria. Si algo sale mal, el servidor web no se entera.

En Linux/macOS los límites de CPU y memoria los pone `resource`; en Windows solo
hay límite de tiempo (resource no existe ahí).
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

from .error_handler import _explicacion

logger = logging.getLogger("tortuscript.proceso")

RAIZ = Path(__file__).resolve().parent.parent
TIEMPO_MAX = 10           # segundos reales (incluye arrancar Python: un antivirus puede demorarlo).
                          # Los bucles infinitos no llegan acá: los corta el límite de pasos en ~0,1 s.
CPU_MAX = 4               # segundos de CPU
MEMORIA_MAX = 512 * 1024 * 1024


def _limitar():
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_MAX, CPU_MAX))
    resource.setrlimit(resource.RLIMIT_AS, (MEMORIA_MAX, MEMORIA_MAX))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))      # no puede escribir archivos


def _falla(tipo, detalle=""):
    return {"error": True, "salida": "", "salida_programa": "", "entradas": [],
            "pregunta": None, "tipo": None, "python": "",
            "mensaje": _explicacion(tipo, detalle)}


def correr(pedido):
    """Ejecuta el pedido en un proceso hijo y devuelve el dict de respuesta."""
    opciones = {}
    if sys.platform != "win32":
        opciones["preexec_fn"] = _limitar
    try:
        r = subprocess.run(
            [sys.executable, "-m", "tortuscript.worker"],
            input=json.dumps(pedido, ensure_ascii=False), capture_output=True,
            text=True, encoding="utf-8", timeout=TIEMPO_MAX, cwd=str(RAIZ), **opciones)
    except subprocess.TimeoutExpired:
        return _falla("TardoDemasiado")
    if r.returncode != 0 or not r.stdout.strip():
        # Muerto por límite de CPU (SIGXCPU) o de memoria, o un error interno
        logger.warning("worker terminó con código %s: %s", r.returncode, r.stderr[-500:])
        if "MemoryError" in r.stderr:
            return _falla("SinMemoria")
        return _falla("TardoDemasiado" if r.returncode < 0 else "Interno")
    try:
        return json.loads(r.stdout)
    except ValueError:
        logger.error("respuesta ilegible del worker: %r", r.stdout[-300:])
        return _falla("Interno")
