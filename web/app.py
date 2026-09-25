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
from datetime import date
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from tortuscript import contenido, evaluacion, leccion as motor, progreso  # noqa: E402
from tortuscript.ejercicios import EJERCICIOS  # noqa: E402
from tortuscript.proceso import correr  # noqa: E402
from tortuscript.referencia import cargar_referencia  # noqa: E402
from tortuscript.repaso import MODOS, cola_repaso, contar  # noqa: E402
from tortuscript.translator import TraductorTortuScript, detectar_tipo  # noqa: E402

logger = logging.getLogger("tortuscript.web")
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}


def create_app(token=None):
    app = Flask(__name__)
    app.config["TOKEN"] = token or secrets.token_urlsafe(24)
    app.config["JSON_AS_ASCII"] = False
    # Pistas vistas por (perfil, ejercicio): se reinician al abrir el ejercicio.
    pistas_vistas = {}
    INDICES_POR_LECCION = {}
    for i, e in enumerate(EJERCICIOS):
        INDICES_POR_LECCION.setdefault(e["leccion_id"], []).append(i)
    intentos = {}    # errores y respuesta vista por (perfil, lección, paso); se reinicia al abrir la lección
    colas = {}       # colas de repaso fijadas al empezar: (perfil, modo, semilla) -> [índices]

    # ─────────────── seguridad ───────────────
    @app.before_request
    def _proteger():
        if request.host.split(":")[0] not in HOSTS_PERMITIDOS:
            abort(403)
        if request.path.startswith("/api/") and \
                request.headers.get("X-Tortu-Token") != app.config["TOKEN"]:
            abort(403)

    @app.before_request
    def _bienvenida():
        """Un perfil nuevo empieza por la bienvenida (nombre, experiencia y meta diaria)."""
        if request.method != "GET" or request.endpoint in (None, "static", "bienvenida") \
                or request.path.startswith("/api/"):
            return None
        if progreso.necesita_onboarding(progreso.cargar_progreso()):
            return redirect(url_for("bienvenida"))
        return None

    @app.context_processor
    def _globales():
        return {"token": app.config["TOKEN"], "estado": _estado(), "perfil": progreso.PERFIL_ACTUAL}

    # ─────────────── helpers ───────────────
    def _estado():
        p = progreso.cargar_progreso()
        xp = p.get("xp_total", 0)
        nivel, xp_actual, xp_max = progreso.calcular_nivel(xp)
        completados = [int(k) for k, v in p["ejercicios"].items() if v.get("completado")]
        camino = motor.estado_camino(_curso(), p, INDICES_POR_LECCION)
        planas = [lec for seccion in camino for lec in seccion["lecciones"]]
        meta = progreso.meta_diaria_xp(p)
        hoy_xp = progreso.xp_de_hoy(p)
        return {
            "lecciones_hechas": sum(1 for lec in planas if lec["estado"] in ("hecha", "perfecta")),
            "lecciones_total": len(planas),
            "xp_hoy": hoy_xp, "meta_xp": meta, "meta_min": p["config"]["meta_min"],
            "meta_pct": min(100, round(100 * hoy_xp / meta)) if meta else 0,
            "nombre": p["config"].get("nombre") or progreso.PERFIL_ACTUAL,
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

    def _niveles():
        return {s["nivel"]: s["titulo"] for s in contenido.cargar_curso()["secciones"]}

    def _pagina_ejercicio(indice, repaso=None):
        ej = _ejercicio_o_404(indice)
        pistas_vistas[(progreso.PERFIL_ACTUAL, indice)] = 0
        hallada = motor.buscar_leccion(_curso(), ej.get("leccion_id"))
        leccion_larga = hallada[1]["id"] if hallada and len(hallada[1]["pasos"]) > 1 else None
        return render_template("ejercicio.html", ej=ej, n=indice + 1, total=len(EJERCICIOS), repaso=repaso,
                               leccion_larga=leccion_larga)

    def _curso():
        return contenido.cargar_curso()

    def _leccion_o_404(leccion_id):
        hallada = motor.buscar_leccion(_curso(), leccion_id)
        if hallada is None:
            abort(404)
        return hallada

    def _completada(leccion, p=None):
        p = p or progreso.cargar_progreso()
        indices = contenido.indices_ejercicio(leccion["id"]).values()
        return motor.esta_completada(p, leccion["id"], list(indices))

    def _leccion_desbloqueada(posicion, p=None):
        if posicion == 0:
            return True
        p = p or progreso.cargar_progreso()
        anterior = motor.lista_lecciones(_curso())[posicion - 1]
        return _completada(anterior, p)

    def _resumen_leccion(leccion_id, info):
        """Lo que la página necesita saber al terminar (o no) una lección."""
        siguiente = motor.leccion_siguiente(_curso(), leccion_id)
        return {**info, "siguiente": siguiente["id"] if siguiente else None,
                "titulo_siguiente": siguiente["titulo"] if siguiente else None}

    def _ejecutar_para_motor(fuente, entradas):
        """Lo que muestra un programa, o None si falla o pregunta algo (lo usa 'ordenar'/'completar')."""
        r = correr({"op": "ejecutar", "fuente": fuente, "entradas": entradas})
        return None if r.get("error") or r.get("pregunta") is not None else r.get("salida_programa", "")

    # ─────────────── páginas ───────────────
    @app.get("/")
    def inicio():
        p = progreso.cargar_progreso()
        camino = motor.estado_camino(_curso(), p, INDICES_POR_LECCION)
        actual = next((lec for seccion in camino for lec in seccion["lecciones"] if lec["estado"] == "actual"), None)
        return render_template("inicio.html", camino=camino, actual=actual)

    @app.get("/aprender")
    def aprender():
        """Va directo a la lección que toca (o a la última si ya terminó todo)."""
        camino = motor.estado_camino(_curso(), progreso.cargar_progreso(), INDICES_POR_LECCION)
        planas = [lec for seccion in camino for lec in seccion["lecciones"]]
        destino = next((l for l in planas if l["estado"] == "actual"), planas[-1])
        return redirect(url_for("leccion", leccion_id=destino["id"]))

    @app.get("/bienvenida")
    def bienvenida():
        return render_template("bienvenida.html", metas=progreso.METAS_MIN, xp_por_minuto=progreso.XP_POR_MINUTO)

    @app.get("/ejercicios")
    def ejercicios_siguiente():
        return redirect(url_for("ejercicio", n=_siguiente_pendiente() + 1))

    @app.get("/ejercicios/<int:n>")
    def ejercicio(n):
        indice = n - 1
        ej = _ejercicio_o_404(indice)
        if not _desbloqueado(indice):
            return redirect(url_for("ejercicio", n=_siguiente_pendiente() + 1))
        return _pagina_ejercicio(indice)

    @app.get("/leccion/<leccion_id>")
    def leccion(leccion_id):
        seccion, lec, posicion = _leccion_o_404(leccion_id)
        p = progreso.cargar_progreso()
        if not _leccion_desbloqueada(posicion, p):
            return redirect(url_for("ejercicios_siguiente"))
        for i in range(len(lec["pasos"])):
            intentos.pop((progreso.PERFIL_ACTUAL, leccion_id, i), None)
        ejercicios_de = contenido.indices_ejercicio(leccion_id)
        pasos = [motor.paso_publico(paso, leccion_id, i, ejercicios_de[i] + 1 if i in ejercicios_de else None)
                 for i, paso in enumerate(lec["pasos"])]
        for ej_n in [x["ejercicio"] for x in pasos if x["tipo"] == "escribir"]:
            pistas_vistas[(progreso.PERFIL_ACTUAL, ej_n - 1)] = 0
        datos = {"id": leccion_id, "titulo": lec["titulo"], "seccion": seccion["titulo"],
                 "nivel": seccion["nivel"], "pasos": pasos,
                 "ya_completada": _completada(lec, p)}
        return render_template("leccion.html", datos=datos, titulo=lec["titulo"])

    @app.get("/mapa")
    def mapa():
        p = progreso.cargar_progreso()
        datos = p["ejercicios"]
        niveles = {}
        for i, ej in enumerate(EJERCICIOS):
            d = datos.get(str(i), {})
            numero, _, nombre = ej["titulo"].partition(". ")
            niveles.setdefault(ej["nivel"], []).append({
                "n": i + 1, "leccion": ej["leccion_id"], "numero": numero, "nombre": nombre or ej["titulo"],
                "completado": bool(d.get("completado")), "estrellas": d.get("estrellas", 0),
                "xp": d.get("xp", 0), "abierto": bool(_desbloqueado(i, p)),
            })
        tres = sum(1 for d in datos.values() if d.get("estrellas", 0) == 3)
        return render_template("mapa.html", niveles=niveles, nombres=_niveles(), tres_estrellas=tres)

    @app.get("/resumen")
    def resumen():
        p = progreso.cargar_progreso()
        hoy = progreso.resumen_sesion_hoy(p, EJERCICIOS)
        return render_template(
            "resumen.html", hoy=hoy, racha=progreso.racha_vigente(p), racha_max=p.get("racha_max", 0),
            jugo_hoy=p.get("ultimo_dia") == str(date.today()), calendario=progreso.calendario_semana(p),
            estrellas_texto=progreso.estrellas_texto, metas=progreso.METAS_MIN)

    @app.get("/referencia")
    def referencia():
        return render_template("referencia.html", ref=cargar_referencia())

    @app.get("/repaso")
    def repaso():
        completados, imperfectos = contar(progreso.cargar_progreso(), len(EJERCICIOS))
        return render_template("repaso.html", modos=MODOS, completados=completados, imperfectos=imperfectos)

    def _cola_o_404(modo, semilla, nueva=False):
        """La cola se fija al empezar el repaso: si un ejercicio pasa a 3 estrellas a mitad
        de camino, no desaparece de la lista ni se corren los lugares."""
        if modo not in MODOS:
            abort(404)
        clave = (progreso.PERFIL_ACTUAL, modo, semilla)
        if nueva or clave not in colas:
            colas[clave] = cola_repaso(progreso.cargar_progreso(), modo, len(EJERCICIOS), semilla)
        return colas[clave]

    @app.get("/repaso/<modo>")
    def repaso_modo(modo):
        semilla = request.args.get("s", type=int)
        if semilla is None:
            semilla = secrets.randbelow(10**6)
        _cola_o_404(modo, semilla, nueva=True)
        return redirect(url_for("repaso_paso", modo=modo, pos=1, s=semilla))

    @app.get("/repaso/<modo>/<int:pos>")
    def repaso_paso(modo, pos):
        semilla = request.args.get("s", 0, type=int)
        cola = _cola_o_404(modo, semilla)
        if not cola:
            return render_template("repaso_fin.html", modo=modo, modos=MODOS, total=0)
        if pos > len(cola):
            return render_template("repaso_fin.html", modo=modo, modos=MODOS, total=len(cola))
        if pos < 1:
            abort(404)
        anterior = url_for("repaso_paso", modo=modo, pos=pos - 1, s=semilla) if pos > 1 else None
        siguiente = url_for("repaso_paso", modo=modo, pos=pos + 1, s=semilla)
        return _pagina_ejercicio(cola[pos - 1], repaso={
            "modo": MODOS[modo][1], "pos": pos, "total": len(cola),
            "anterior": anterior, "siguiente": siguiente, "ultimo": pos == len(cola)})

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

    def _paso_o_404(leccion_id, i):
        _, lec, _ = _leccion_o_404(leccion_id)
        if not 0 <= i < len(lec["pasos"]):
            abort(404)
        return lec, lec["pasos"][i]

    @app.post("/api/lecciones/<leccion_id>/pasos/<int:i>/comprobar")
    def api_comprobar_paso(leccion_id, i):
        lec, paso = _paso_o_404(leccion_id, i)
        if paso["tipo"] == "escribir":
            abort(400)                           # se evalúa ejecutando: /api/ejercicios/<n>/evaluar
        clave = (progreso.PERFIL_ACTUAL, leccion_id, i)
        estado_paso = intentos.setdefault(clave, {"errores": 0, "revelado": False})
        r = motor.comprobar(paso, (request.get_json(silent=True) or {}).get("respuesta"), _ejecutar_para_motor)
        if not r["ok"]:
            estado_paso["errores"] += 1
            return jsonify(ok=False, pista=r["pista"], malos=r["malos"],
                           puede_ver_respuesta=motor.puede_ver_respuesta(estado_paso["errores"]))
        p = progreso.cargar_progreso()
        nivel_antes = progreso.calcular_nivel(p.get("xp_total", 0))[0]
        xp = 0 if paso["tipo"] == "explicacion" else motor.xp_por_intentos(estado_paso["errores"] + 1, False)
        perfecto = estado_paso["errores"] == 0
        info = progreso.registrar_paso_leccion(p, leccion_id, i, xp, perfecto, len(lec["pasos"]))
        return jsonify(ok=True, xp=info["xp_ganado"], perfecto=perfecto,
                       sube_nivel=progreso.calcular_nivel(p["xp_total"])[0] > nivel_antes,
                       leccion=_resumen_leccion(leccion_id, info), estado_juego=_estado())

    @app.post("/api/lecciones/<leccion_id>/pasos/<int:i>/respuesta")
    def api_ver_respuesta(leccion_id, i):
        lec, paso = _paso_o_404(leccion_id, i)
        if paso["tipo"] in ("escribir", "explicacion"):
            abort(400)
        clave = (progreso.PERFIL_ACTUAL, leccion_id, i)
        estado_paso = intentos.setdefault(clave, {"errores": 0, "revelado": False})
        if not motor.puede_ver_respuesta(estado_paso["errores"]):
            abort(403)                           # primero hay que intentarlo (2 errores)
        estado_paso["revelado"] = True
        p = progreso.cargar_progreso()
        info = progreso.registrar_paso_leccion(p, leccion_id, i, 0, False, len(lec["pasos"]))
        return jsonify(respuesta=motor.respuesta_correcta(paso), leccion=_resumen_leccion(leccion_id, info),
                       estado_juego=_estado())

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
            lec_id, paso_i = ej.get("leccion_id"), ej.get("paso")
            hallada = motor.buscar_leccion(_curso(), lec_id) if lec_id else None
            if hallada is not None and paso_i is not None:     # el paso 'escribir' de su lección
                info = progreso.registrar_paso_leccion(p, lec_id, paso_i, 0, estrellas == 3, len(hallada[1]["pasos"]))
                r["leccion"] = _resumen_leccion(lec_id, info)
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

    @app.post("/api/onboarding")
    def api_onboarding():
        datos = request.get_json(silent=True) or {}
        crudo = str(datos.get("nombre") or "").strip()
        if crudo:
            perfil = progreso.sanitizar_perfil(crudo)
            if not perfil:
                return jsonify(ok=False, mensaje="Usá letras o números para el nombre."), 400
            if perfil != progreso.PERFIL_ACTUAL:
                progreso.set_perfil(perfil)
                progreso.recordar_perfil(perfil)
        p = progreso.cargar_progreso()
        ok = progreso.guardar_config(p, experiencia=datos.get("experiencia"), meta_min=datos.get("meta_min"),
                                     nombre=crudo or None, onboarding=True)
        if not ok:
            return jsonify(ok=False, mensaje="Alguna respuesta no es válida."), 400
        return jsonify(ok=True, actual=progreso.PERFIL_ACTUAL, estado=_estado())

    @app.post("/api/config")
    def api_config():
        datos = request.get_json(silent=True) or {}
        p = progreso.cargar_progreso()
        if not progreso.guardar_config(p, meta_min=datos.get("meta_min")):
            return jsonify(ok=False, mensaje="Esa meta no existe."), 400
        return jsonify(ok=True, estado=_estado())

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
