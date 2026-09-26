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
import threading
from datetime import date
from pathlib import Path

from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from tortuscript import contenido, evaluacion, leccion as motor, liga, logros, progreso  # noqa: E402
from tortuscript import practica as espaciado  # noqa: E402
from tortuscript import proyectos as mis_proyectos  # noqa: E402
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
    # Pistas vistas por (perfil, lección, paso): se reinician al abrir el ejercicio o la lección.
    pistas_vistas = {}
    INDICES_POR_LECCION = {}
    for i, e in enumerate(EJERCICIOS):
        INDICES_POR_LECCION.setdefault(e["leccion_id"], []).append(i)
    intentos = {}    # errores y respuesta vista por (perfil, lección, paso); se reinicia al abrir la lección
    practicas = {}   # sesión de práctica del día por perfil: {"dia", "pasos": [(lección, paso)]}
    colas = {}       # colas de repaso fijadas al empezar: (perfil, modo, semilla) -> [índices]
    turno = threading.RLock()     # los pedidos van de a uno: cargar → modificar → guardar el progreso no se pisa

    # ─────────────── seguridad ───────────────
    @app.before_request
    def _proteger():
        if request.host.split(":")[0] not in HOSTS_PERMITIDOS:
            abort(403)
        if request.path.startswith("/api/") and \
                request.headers.get("X-Tortu-Token") != app.config["TOKEN"]:
            abort(403)

    @app.before_request
    def _de_a_uno():
        """Dos pestañas (o dos toques seguidos) no pueden leer el mismo progreso y pisarse al guardar.
        Todo pedido de página o de API espera su turno; los archivos estáticos no."""
        if request.endpoint in (None, "static"):
            return None
        turno.acquire()
        g.con_turno = True
        return None

    @app.teardown_request
    def _soltar_turno(_error):
        if g.pop("con_turno", False):
            turno.release()

    @app.before_request
    def _bienvenida():
        """Un perfil nuevo empieza por la bienvenida (nombre, experiencia y meta diaria)."""
        if request.method != "GET" or request.endpoint in (None, "static", "bienvenida") \
                or request.path.startswith("/api/"):
            return None
        if progreso.necesita_onboarding(progreso.cargar_progreso()):
            return redirect(url_for("bienvenida"))
        return None

    @app.before_request
    def _semana_de_la_liga():
        """Al cambiar de semana se resuelve la liga anterior (¿subió?) una sola vez."""
        if request.method != "GET" or request.endpoint in (None, "static") or request.path.startswith("/api/"):
            return None
        p = progreso.cargar_progreso()
        viejo = dict(p.get("liga") or {})

        def otros_de_la_semana(domingo):
            return {n: xp for n, dias in progreso.leer_otros_perfiles().items()
                    if (xp := liga.xp_de_la_semana(dias, domingo)) > 0}
        liga.cerrar_semana(p, otros_de_la_semana, date.today())
        if p.get("liga") != viejo or p.get("avisos"):
            progreso.guardar_progreso(p)
        return None

    @app.context_processor
    def _globales():
        # Lo que quedó pendiente (p. ej. subir de liga al cambiar la semana) se cuenta en la próxima página
        avisos = progreso.tomar_avisos(progreso.cargar_progreso())
        return {"token": app.config["TOKEN"], "estado": _estado(), "perfil": progreso.PERFIL_ACTUAL,
                "avisos_pendientes": avisos, "ajustes": progreso.ajustes_de(progreso.cargar_progreso())}

    # ─────────────── helpers ───────────────
    def _estado():
        p = progreso.cargar_progreso()
        xp = p.get("xp_total", 0)
        nivel, xp_actual, xp_max = progreso.calcular_nivel(xp)
        completados = [int(k) for k, v in p["ejercicios"].items() if v.get("completado")]
        planas = motor.lecciones_planas(_camino(p))
        meta = progreso.meta_diaria_xp(p)
        hoy_xp = progreso.xp_de_hoy(p)
        reto = progreso.reto_de_racha(p)
        tabla_liga = liga.resumen(p, _otros_en_liga(date.today()), date.today())
        return {
            "congeladores": p.get("congeladores", 0), "racha_protegida": progreso.racha_protegida(p),
            "reto_dias": reto[0], "reto_total": reto[1],
            "logros_ganados": len(p.get("logros", {})), "logros_total": len(logros.LOGROS),
            "practica_pendientes": espaciado.pendientes(p, _cursos(), date.today()),
            "liga": {k: tabla_liga[k] for k in ("liga", "icono", "puesto", "tamano", "xp", "dias_restantes", "asciende")},
            "lecciones_hechas": sum(1 for lec in planas if lec["estado"] in ("hecha", "perfecta")),
            "lecciones_total": len(planas),
            "xp_hoy": hoy_xp, "meta_xp": meta, "meta_min": p["config"]["meta_min"],
            "meta_pct": min(100, round(100 * hoy_xp / meta)) if meta else 0,
            "nombre": p["config"].get("nombre") or progreso.PERFIL_ACTUAL,
            "xp": xp, "nivel": nivel, "titulo": progreso.titulo_nivel(nivel),
            "color_tortuga": progreso.color_tortuga(nivel),
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

    def _otros_en_liga(dia):
        """XP de la semana (hasta `dia`) de los otros perfiles de la PC que jugaron esta semana."""
        return {n: xp for n, dias in progreso.leer_otros_perfiles().items()
                if (xp := liga.xp_de_la_semana(dias, dia)) > 0}

    def _avisos_tras(p):
        """Revisa los logros con el progreso ya actualizado y devuelve (y guarda) los avisos pendientes."""
        logros.revisar(p, logros.resumen_de(p, _camino(p)))
        return progreso.tomar_avisos(p)

    def _niveles():
        return {s["nivel"]: s["titulo"] for s in contenido.cargar_curso()["secciones"]}

    def _pagina_ejercicio(indice, repaso=None):
        ej = _ejercicio_o_404(indice)
        pistas_vistas[(progreso.PERFIL_ACTUAL, ej["leccion_id"], ej["paso"])] = 0
        hallada = motor.buscar_leccion(_curso(), ej.get("leccion_id"))
        leccion_larga = hallada[1]["id"] if hallada and len(hallada[1]["pasos"]) > 1 else None
        return render_template("ejercicio.html", ej=ej, n=indice + 1, total=len(EJERCICIOS), repaso=repaso,
                               leccion_larga=leccion_larga)

    def _curso():
        """El curso de los ejercicios clásicos: el índice de cada 'escribir' es la clave de su progreso."""
        return contenido.cargar_curso()

    def _cursos():
        return contenido.todos_los_cursos()

    def _camino(p=None):
        return motor.estado_cursos(_cursos(), p or progreso.cargar_progreso(), INDICES_POR_LECCION)

    def _leccion_o_404(leccion_id):
        hallada = motor.buscar_en_cursos(_cursos(), leccion_id)
        if hallada is None:
            abort(404)
        return hallada                                          # (curso, sección, lección)

    def _completada(leccion, p=None):
        p = p or progreso.cargar_progreso()
        return motor.esta_completada(p, leccion["id"], INDICES_POR_LECCION.get(leccion["id"], []))

    def _leccion_desbloqueada(leccion_id, p=None):
        return any(l["id"] == leccion_id and l["estado"] != "bloqueada"
                   for l in motor.lecciones_planas(_camino(p)))

    def _resumen_leccion(leccion_id, info):
        """Lo que la página necesita saber al terminar (o no) una lección."""
        siguiente = motor.siguiente_global(_cursos(), leccion_id)
        return {**info, "siguiente": siguiente["id"] if siguiente else None,
                "titulo_siguiente": siguiente["titulo"] if siguiente else None}

    def _ejecutar_para_motor(paso):
        """Cómo el motor corre un programa para comparar (completar/ordenar): devuelve
        {"salida", "ordenes"}, o None si falla o pregunta algo."""
        op = "tortuga" if paso.get("tortuga") else "ejecutar"

        def ejecutar(fuente, entradas):
            r = correr({"op": op, "fuente": fuente, "entradas": entradas})
            if r.get("error") or r.get("pregunta") is not None:
                return None
            return {"salida": r.get("salida_programa", ""), "ordenes": r.get("ordenes", [])}
        return ejecutar

    objetivos = {}   # dibujo de la solución de cada paso de tortuga: (fuente, entradas) -> órdenes

    def _objetivo(paso):
        clave = (paso["solucion"] if paso["tipo"] == "escribir" else "\n".join(paso.get("lineas") or [])
                 or _completado_oficial(paso), tuple(paso.get("entradas_prueba") or ()))
        if clave not in objetivos:
            r = correr({"op": "tortuga", "fuente": clave[0], "entradas": list(clave[1])})
            objetivos[clave] = [] if r.get("error") else r.get("ordenes", [])
        return objetivos[clave]

    def _completado_oficial(paso):
        codigo = paso.get("codigo", "")
        for r in paso.get("respuesta", []):
            codigo = codigo.replace("___", r, 1)
        return codigo

    def _publico(paso, leccion_id, i):
        """El paso listo para el navegador (+ el dibujo objetivo de los pasos de tortuga)."""
        ejercicio = contenido.indices_ejercicio(leccion_id).get(i)
        publico = motor.paso_publico(paso, leccion_id, i, None if ejercicio is None else ejercicio + 1)
        if paso.get("tortuga") and paso["tipo"] in ("escribir", "completar", "ordenar") and not paso.get("laberinto"):
            publico["objetivo"] = _objetivo(paso)          # en un laberinto no hay dibujo objetivo: vale cualquier camino
        return publico

    # ─────────────── páginas ───────────────
    @app.get("/")
    def inicio():
        camino = _camino()
        return render_template("inicio.html", camino=camino, actual=motor.leccion_actual(camino))

    @app.get("/aprender")
    def aprender():
        """Va directo a la lección que toca (o a la última si ya terminó todo)."""
        planas = motor.lecciones_planas(_camino())
        destino = motor.leccion_actual(_camino()) or planas[-1]
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
        _ejercicio_o_404(indice)
        if not _desbloqueado(indice):
            return redirect(url_for("ejercicio", n=_siguiente_pendiente() + 1))
        return _pagina_ejercicio(indice)

    @app.get("/leccion/<leccion_id>")
    def leccion(leccion_id):
        curso, seccion, lec = _leccion_o_404(leccion_id)
        p = progreso.cargar_progreso()
        if not _leccion_desbloqueada(leccion_id, p):
            return redirect(url_for("aprender"))
        for i in range(len(lec["pasos"])):
            intentos.pop((progreso.PERFIL_ACTUAL, leccion_id, i), None)
            pistas_vistas.pop((progreso.PERFIL_ACTUAL, leccion_id, i), None)
        datos = {"id": leccion_id, "titulo": lec["titulo"], "seccion": seccion["titulo"], "curso": curso["titulo"],
                 "nivel": seccion["nivel"], "pasos": [_publico(paso, leccion_id, i) for i, paso in enumerate(lec["pasos"])],
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
            estrellas_texto=progreso.estrellas_texto, metas=progreso.METAS_MIN,
            recientes=sorted((c for c in logros.catalogo(p) if c["ganado"]), key=lambda c: c["fecha"], reverse=True)[:4])

    @app.get("/practica")
    def practica():
        """Práctica del día: hasta 6 tarjetas que ya tocan, de lecciones distintas (repaso espaciado)."""
        p = progreso.cargar_progreso()
        elegidas = espaciado.elegir(p, _cursos(), date.today())
        if not elegidas:
            return render_template("practica_vacia.html")
        practicas[progreso.PERFIL_ACTUAL] = {"dia": str(date.today()), "pasos": elegidas}
        pasos = []
        for leccion_id, i in elegidas:
            _, _, lec = _leccion_o_404(leccion_id)
            intentos.pop((progreso.PERFIL_ACTUAL, "practica", leccion_id, i), None)
            publico = _publico(lec["pasos"][i], leccion_id, i)
            publico["leccion"] = leccion_id
            pasos.append(publico)
        datos = {"id": "practica", "modo": "practica", "titulo": "Práctica del día", "seccion": "Repaso espaciado",
                 "nivel": None, "pasos": pasos, "ya_completada": False}
        return render_template("leccion.html", datos=datos, titulo="Práctica del día")

    @app.get("/certificado/<curso_id>")
    def certificado(curso_id):
        """Diploma imprimible (o para guardar como PDF) al terminar un curso. Gratis y sin cuentas."""
        p = progreso.cargar_progreso()
        curso = next((c for c in _camino(p) if c["id"] == curso_id), None)
        if curso is None:
            abort(404)
        if not curso["completo"]:
            return redirect(url_for("inicio"))
        return render_template("certificado.html", curso=curso, hoy=date.today(), xp=p.get("xp_total", 0),
                               nombre=p["config"].get("nombre") or progreso.PERFIL_ACTUAL)

    @app.get("/logros")
    def pagina_logros():
        p = progreso.cargar_progreso()
        return render_template("logros.html", catalogo=logros.catalogo(p),
                               diplomas=[c for c in _camino(p) if c["completo"]])

    @app.get("/liga")
    def pagina_liga():
        p = progreso.cargar_progreso()
        return render_template("liga.html", liga=liga.resumen(p, _otros_en_liga(date.today()), date.today()),
                               ligas=liga.LIGAS)

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

    def _proyecto_pedido(tipo):
        """El proyecto de ?proyecto=<id>: (proyecto|None, redirección|None). Si es de otro tipo, va a su página."""
        pedido = request.args.get("proyecto")
        if not pedido:
            return None, None
        p = mis_proyectos.obtener(progreso.cargar_progreso(), pedido)
        if p is None:
            return None, redirect(url_for(tipo))
        if p["tipo"] != tipo:
            return None, redirect(url_for(p["tipo"], proyecto=pedido))
        return p, None

    @app.get("/experimentar")
    def experimentar():
        proyecto, otra = _proyecto_pedido("experimentar")
        return otra or render_template("experimentar.html", proyecto=proyecto)

    @app.get("/tortuga")
    def tortuga():
        proyecto, otra = _proyecto_pedido("tortuga")
        return otra or render_template("tortuga.html", proyecto=proyecto)

    @app.get("/proyectos")
    def proyectos():
        return render_template("proyectos.html", proyectos=mis_proyectos.listar(progreso.cargar_progreso()),
                               maximo=mis_proyectos.MAX_PROYECTOS)

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
        _, _, lec = _leccion_o_404(leccion_id)
        if not 0 <= i < len(lec["pasos"]):
            abort(404)
        if not _leccion_desbloqueada(leccion_id):
            abort(403)
        return lec, lec["pasos"][i]

    @app.post("/api/lecciones/<leccion_id>/pasos/<int:i>/comprobar")
    def api_comprobar_paso(leccion_id, i):
        lec, paso = _paso_o_404(leccion_id, i)
        if paso["tipo"] == "escribir":
            abort(400)                           # se evalúa ejecutando: .../evaluar
        clave = (progreso.PERFIL_ACTUAL, leccion_id, i)
        estado_paso = intentos.setdefault(clave, {"errores": 0, "revelado": False})
        r = motor.comprobar(paso, (request.get_json(silent=True) or {}).get("respuesta"), _ejecutar_para_motor(paso))
        if not r["ok"]:
            estado_paso["errores"] += 1
            return jsonify(ok=False, pista=r["pista"], malos=r["malos"],
                           puede_ver_respuesta=motor.puede_ver_respuesta(estado_paso["errores"]))
        p = progreso.cargar_progreso()
        nivel_antes = progreso.calcular_nivel(p.get("xp_total", 0))[0]
        xp = 0 if paso["tipo"] == "explicacion" else motor.xp_por_intentos(estado_paso["errores"] + 1, False)
        perfecto = estado_paso["errores"] == 0
        info = progreso.registrar_paso_leccion(p, leccion_id, i, xp, perfecto, len(lec["pasos"]))
        avisos = _avisos_tras(p)
        return jsonify(ok=True, xp=info["xp_ganado"], perfecto=perfecto,
                       sube_nivel=progreso.calcular_nivel(p["xp_total"])[0] > nivel_antes,
                       leccion=_resumen_leccion(leccion_id, info), estado_juego=_estado(), avisos=avisos)

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
                       estado_juego=_estado(), avisos=_avisos_tras(p))

    def _evaluar_escribir(leccion_id, i, paso, datos):
        """Ejecuta y evalúa un paso 'escribir'. Los ejercicios del curso clásico guardan su
        resultado en `ejercicios` (clave histórica); los de otros cursos, en el paso de la lección."""
        pedido = {"op": "evaluar_tortuga" if paso.get("tortuga") else "evaluar", "fuente": datos.get("codigo", ""),
                  "entradas": datos.get("entradas", []), "solucion": paso["solucion"]}
        if paso.get("laberinto"):
            pedido.update(laberinto=paso["laberinto"], usar=paso.get("usar") or [])
        r = correr(pedido)
        ev = r.get("evaluacion")
        if ev and ev.get("objetivo") is not None:
            ev.pop("objetivo")                   # el dibujo objetivo ya está en la página
        if ev and ev["estado"] == evaluacion.CORRECTO:
            _, _, lec = _leccion_o_404(leccion_id)
            vistas = pistas_vistas.get((progreso.PERFIL_ACTUAL, leccion_id, i), 0)
            estrellas, xp = evaluacion.estrellas_por_pistas(vistas)
            p = progreso.cargar_progreso()
            nivel_antes = progreso.calcular_nivel(p.get("xp_total", 0))[0]
            indice = contenido.indices_ejercicio(leccion_id).get(i)
            if indice is not None:
                mejora = progreso.registrar_ejercicio(p, indice, estrellas, xp)
                info = progreso.registrar_paso_leccion(p, leccion_id, i, 0, estrellas == 3, len(lec["pasos"]))
            else:
                info = progreso.registrar_paso_leccion(p, leccion_id, i, xp, estrellas == 3, len(lec["pasos"]),
                                                       estrellas=estrellas)
                mejora = info["xp_ganado"] > 0
            r["premio"] = {"estrellas": estrellas, "xp": xp, "mejora": mejora,
                           "sube_nivel": progreso.calcular_nivel(p["xp_total"])[0] > nivel_antes}
            r["leccion"] = _resumen_leccion(leccion_id, info)
            r["avisos"] = _avisos_tras(p)
        r["estado_juego"] = _estado()
        return r

    def _dar_pista(leccion_id, i, paso):
        clave = (progreso.PERFIL_ACTUAL, leccion_id, i)
        nivel = min(pistas_vistas.get(clave, 0) + 1, 3)
        pistas_vistas[clave] = nivel
        sol = paso["solucion"].strip()
        lineas = sol.split("\n")
        if nivel == 1:
            palabras = paso.get("palabras_pista") or evaluacion.palabras_clave(sol)
            contenido_pista = {"titulo": "Palabras clave a usar", "texto": ", ".join(palabras)}
        elif nivel == 2:
            contenido_pista = {"titulo": "La primera línea es", "codigo": lineas[0],
                               "texto": f"En total son {len(lineas)} línea{'s' if len(lineas) != 1 else ''}."}
        else:
            contenido_pista = {"titulo": "Solución completa", "codigo": sol}
            if paso.get("lenguaje") != "python":
                contenido_pista["python"] = TraductorTortuScript().traducir_codigo(sol)
        return jsonify(nivel=nivel, **contenido_pista)

    @app.post("/api/lecciones/<leccion_id>/pasos/<int:i>/evaluar")
    def api_evaluar_paso(leccion_id, i):
        lec, paso = _paso_o_404(leccion_id, i)
        if paso["tipo"] != "escribir":
            abort(400)
        return jsonify(_evaluar_escribir(leccion_id, i, paso, request.get_json(silent=True) or {}))

    @app.post("/api/lecciones/<leccion_id>/pasos/<int:i>/pista")
    def api_pista_paso(leccion_id, i):
        lec, paso = _paso_o_404(leccion_id, i)
        if paso["tipo"] != "escribir":
            abort(400)
        return _dar_pista(leccion_id, i, paso)

    # Ejercicios clásicos (/ejercicios/N): mismas reglas, identificados por el índice de su 'escribir'.
    def _ejercicio_como_paso(n):
        ej = _ejercicio_o_404(n - 1)
        _, _, lec = _leccion_o_404(ej["leccion_id"])
        return ej["leccion_id"], ej["paso"], lec["pasos"][ej["paso"]]

    @app.post("/api/ejercicios/<int:n>/evaluar")
    def api_evaluar(n):
        indice = n - 1
        _ejercicio_o_404(indice)
        if not _desbloqueado(indice):
            abort(403)
        leccion_id, i, paso = _ejercicio_como_paso(n)
        return jsonify(_evaluar_escribir(leccion_id, i, paso, request.get_json(silent=True) or {}))

    @app.post("/api/ejercicios/<int:n>/pista")
    def api_pista(n):
        leccion_id, i, paso = _ejercicio_como_paso(n)
        return _dar_pista(leccion_id, i, paso)

    def _tarjeta_de_la_sesion(datos):
        """(leccion_id, indice, paso) si la tarjeta es de la sesión de hoy; si no, 403."""
        try:
            leccion_id, i = str(datos.get("leccion", "")), int(datos.get("paso"))
        except (TypeError, ValueError):
            abort(400)
        sesion = practicas.get(progreso.PERFIL_ACTUAL)
        if not sesion or (leccion_id, i) not in sesion["pasos"]:
            abort(403)
        _, _, lec = _leccion_o_404(leccion_id)
        return leccion_id, i, lec["pasos"][i]

    @app.post("/api/practica/comprobar")
    def api_practica_comprobar():
        datos = request.get_json(silent=True) or {}
        leccion_id, i, paso = _tarjeta_de_la_sesion(datos)
        clave = (progreso.PERFIL_ACTUAL, "practica", leccion_id, i)
        estado_paso = intentos.setdefault(clave, {"errores": 0, "revelado": False})
        r = motor.comprobar(paso, datos.get("respuesta"), _ejecutar_para_motor(paso))
        if not r["ok"]:
            estado_paso["errores"] += 1
            return jsonify(ok=False, pista=r["pista"], malos=r["malos"],
                           puede_ver_respuesta=motor.puede_ver_respuesta(estado_paso["errores"]))
        p = progreso.cargar_progreso()
        nivel_antes = progreso.calcular_nivel(p.get("xp_total", 0))[0]
        acierto = estado_paso["errores"] == 0
        ganado = progreso.registrar_practica(p, leccion_id, i, acierto)
        intentos.pop(clave, None)
        avisos = _avisos_tras(p)
        return jsonify(ok=True, xp=ganado, perfecto=acierto,
                       sube_nivel=progreso.calcular_nivel(p["xp_total"])[0] > nivel_antes,
                       leccion={"siguiente": None}, estado_juego=_estado(), avisos=avisos)

    @app.post("/api/practica/respuesta")
    def api_practica_respuesta():
        datos = request.get_json(silent=True) or {}
        leccion_id, i, paso = _tarjeta_de_la_sesion(datos)
        clave = (progreso.PERFIL_ACTUAL, "practica", leccion_id, i)
        estado_paso = intentos.setdefault(clave, {"errores": 0, "revelado": False})
        if not motor.puede_ver_respuesta(estado_paso["errores"]):
            abort(403)
        estado_paso["revelado"] = True
        p = progreso.cargar_progreso()
        progreso.registrar_practica(p, leccion_id, i, False)
        intentos.pop(clave, None)
        return jsonify(respuesta=motor.respuesta_correcta(paso), leccion={"siguiente": None},
                       estado_juego=_estado(), avisos=_avisos_tras(p))

    def _con_proyectos(accion):
        """Aplica `accion(p)` al progreso; los errores que el chico puede corregir vuelven como 400."""
        p = progreso.cargar_progreso()
        try:
            resultado = accion(p)
        except mis_proyectos.ErrorProyecto as e:
            return jsonify(ok=False, mensaje=str(e)), 400
        progreso.guardar_progreso(p)
        return jsonify(ok=True, id=resultado, total=len(p.get("proyectos", {})), avisos=_avisos_tras(p),
                       estado_juego=_estado())

    @app.post("/api/proyectos")
    def api_proyecto_guardar():
        d = request.get_json(silent=True) or {}
        return _con_proyectos(lambda p: mis_proyectos.guardar(p, d.get("nombre"), d.get("tipo"), d.get("codigo"),
                                                              proyecto_id=d.get("id")))

    @app.post("/api/proyectos/<proyecto_id>/duplicar")
    def api_proyecto_duplicar(proyecto_id):
        return _con_proyectos(lambda p: mis_proyectos.duplicar(p, proyecto_id))

    @app.post("/api/proyectos/<proyecto_id>/borrar")
    def api_proyecto_borrar(proyecto_id):
        return _con_proyectos(lambda p: mis_proyectos.borrar(p, proyecto_id))

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

    @app.post("/api/ajustes")
    def api_ajustes():
        datos = request.get_json(silent=True) or {}
        p = progreso.cargar_progreso()
        cambios = {k: datos.get(k) for k in progreso.AJUSTES if k in datos}
        if not progreso.guardar_ajustes(p, **cambios):
            return jsonify(ok=False, mensaje="Ese ajuste no existe."), 400
        return jsonify(ok=True, ajustes=progreso.ajustes_de(p))

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
