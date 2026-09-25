"""
TortuScript web: servidor Flask local (127.0.0.1) + páginas HTML/CSS/JS.

Seguridad de una app local:
- Solo atiende pedidos con Host 127.0.0.1/localhost (frena "DNS rebinding").
- Toda la API exige el token secreto de esta sesión en el encabezado X-Tortu-Token:
  una página web ajena abierta en el navegador no puede mandarlo (no hay CORS).
- El código del chico nunca corre en este proceso: va a tortuscript.proceso.
"""
import logging
import secrets
import sys
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from tortuscript import evaluacion, progreso  # noqa: E402
from tortuscript.ejercicios import EJERCICIOS  # noqa: E402
from tortuscript.proceso import correr  # noqa: E402
from tortuscript.translator import TraductorTortuScript, detectar_tipo  # noqa: E402

logger = logging.getLogger("tortuscript.web")
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}


def create_app(token=None):
    app = Flask(__name__)
    app.config["TOKEN"] = token or secrets.token_urlsafe(24)
    app.config["JSON_AS_ASCII"] = False
    # Pistas vistas por (perfil, ejercicio): se reinician al abrir el ejercicio.
    pistas_vistas = {}

    # ─────────────── seguridad ───────────────
    @app.before_request
    def _proteger():
        if request.host.split(":")[0] not in HOSTS_PERMITIDOS:
            abort(403)
        if request.path.startswith("/api/") and \
                request.headers.get("X-Tortu-Token") != app.config["TOKEN"]:
            abort(403)

    @app.context_processor
    def _globales():
        return {"token": app.config["TOKEN"], "estado": _estado(), "perfil": progreso.PERFIL_ACTUAL}

    # ─────────────── helpers ───────────────
    def _estado():
        p = progreso.cargar_progreso()
        xp = p.get("xp_total", 0)
        nivel, xp_actual, xp_max = progreso.calcular_nivel(xp)
        completados = [int(k) for k, v in p["ejercicios"].items() if v.get("completado")]
        return {
            "xp": xp, "nivel": nivel, "titulo": progreso.titulo_nivel(nivel),
            "xp_actual": xp_actual, "xp_max": xp_max,
            "racha": progreso.racha_vigente(p),
            "completados": len(completados), "total": len(EJERCICIOS),
            "estrellas": {k: v.get("estrellas", 0) for k, v in p["ejercicios"].items()},
        }

    def _desbloqueado(indice, p=None):
        p = p or progreso.cargar_progreso()
        ej = p["ejercicios"]
        return indice == 0 or ej.get(str(indice), {}).get("completado") or \
            ej.get(str(indice - 1), {}).get("completado")

    def _siguiente_pendiente():
        p = progreso.cargar_progreso()
        return next((i for i in range(len(EJERCICIOS))
                     if not p["ejercicios"].get(str(i), {}).get("completado")), len(EJERCICIOS) - 1)

    def _ejercicio_o_404(n):
        if not 0 <= n < len(EJERCICIOS):
            abort(404)
        return EJERCICIOS[n]

    # ─────────────── páginas ───────────────
    @app.get("/")
    def inicio():
        return render_template("inicio.html", ejercicios=EJERCICIOS)

    @app.get("/ejercicios")
    def ejercicios_siguiente():
        return redirect(url_for("ejercicio", n=_siguiente_pendiente() + 1))

    @app.get("/ejercicios/<int:n>")
    def ejercicio(n):
        indice = n - 1
        ej = _ejercicio_o_404(indice)
        if not _desbloqueado(indice):
            return redirect(url_for("ejercicio", n=_siguiente_pendiente() + 1))
        pistas_vistas[(progreso.PERFIL_ACTUAL, indice)] = 0
        return render_template("ejercicio.html", ej=ej, n=n, total=len(EJERCICIOS))

    @app.get("/experimentar")
    def experimentar():
        return render_template("experimentar.html")

    @app.get("/tortuga")
    def tortuga():
        return render_template("tortuga.html")

    # ─────────────── API ───────────────
    @app.post("/api/traducir")
    def api_traducir():
        fuente = (request.get_json(silent=True) or {}).get("codigo", "")
        tipo = detectar_tipo(fuente)
        python = fuente if tipo == "python" else TraductorTortuScript().traducir_codigo(fuente)
        return jsonify(tipo=tipo, python=python)

    @app.post("/api/ejecutar")
    def api_ejecutar():
        datos = request.get_json(silent=True) or {}
        return jsonify(correr({"op": "ejecutar", "fuente": datos.get("codigo", ""),
                               "entradas": datos.get("entradas", [])}))

    @app.post("/api/tortuga")
    def api_tortuga():
        datos = request.get_json(silent=True) or {}
        return jsonify(correr({"op": "tortuga", "fuente": datos.get("codigo", ""),
                               "entradas": datos.get("entradas", [])}))

    @app.post("/api/ejercicios/<int:n>/evaluar")
    def api_evaluar(n):
        indice = n - 1
        ej = _ejercicio_o_404(indice)
        if not _desbloqueado(indice):
            abort(403)
        datos = request.get_json(silent=True) or {}
        r = correr({"op": "evaluar", "fuente": datos.get("codigo", ""),
                    "entradas": datos.get("entradas", []), "solucion": ej["solucion"]})
        ev = r.get("evaluacion")
        if ev and ev["estado"] == evaluacion.CORRECTO:
            vistas = pistas_vistas.get((progreso.PERFIL_ACTUAL, indice), 0)
            estrellas, xp = evaluacion.estrellas_por_pistas(vistas)
            p = progreso.cargar_progreso()
            nivel_antes = progreso.calcular_nivel(p.get("xp_total", 0))[0]
            mejora = progreso.registrar_ejercicio(p, indice, estrellas, xp)
            r["premio"] = {"estrellas": estrellas, "xp": xp, "mejora": mejora,
                           "sube_nivel": progreso.calcular_nivel(p["xp_total"])[0] > nivel_antes}
        r["estado_juego"] = _estado()
        return jsonify(r)

    @app.post("/api/ejercicios/<int:n>/pista")
    def api_pista(n):
        indice = n - 1
        ej = _ejercicio_o_404(indice)
        clave = (progreso.PERFIL_ACTUAL, indice)
        nivel = min(pistas_vistas.get(clave, 0) + 1, 3)
        pistas_vistas[clave] = nivel
        sol = ej["solucion"].strip()
        lineas = sol.split("\n")
        if nivel == 1:
            contenido = {"titulo": "Palabras clave a usar", "texto": ", ".join(evaluacion.palabras_clave(sol))}
        elif nivel == 2:
            contenido = {"titulo": "La primera línea es", "codigo": lineas[0],
                         "texto": f"En total son {len(lineas)} línea{'s' if len(lineas) != 1 else ''}."}
        else:
            contenido = {"titulo": "Solución completa", "codigo": sol,
                         "python": TraductorTortuScript().traducir_codigo(sol)}
        return jsonify(nivel=nivel, **contenido)

    @app.get("/api/perfiles")
    def api_perfiles():
        return jsonify(actual=progreso.PERFIL_ACTUAL, perfiles=progreso.obtener_perfiles())

    @app.post("/api/perfil")
    def api_perfil():
        nombre = progreso.sanitizar_perfil((request.get_json(silent=True) or {}).get("nombre", ""))
        if not nombre:
            return jsonify(ok=False, mensaje="Usá letras o números para el nombre."), 400
        progreso.set_perfil(nombre)
        progreso.recordar_perfil(nombre)
        if not progreso.get_archivo_progreso(nombre).exists():
            progreso.guardar_progreso(progreso.cargar_progreso(nombre))   # que aparezca en la lista
        return jsonify(ok=True, actual=nombre, estado=_estado())

    @app.get("/api/estado")
    def api_estado():
        return jsonify(_estado())

    progreso.set_perfil(progreso.perfil_recordado())
    return app
