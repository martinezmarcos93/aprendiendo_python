"""Tests de la app web (se saltean si Flask no está instalado)."""
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

try:
    import flask  # noqa: F401
    HAY_FLASK = True
except ImportError:
    HAY_FLASK = False

from tortuscript import progreso


@unittest.skipUnless(HAY_FLASK, "Flask no instalado (pip install -r requirements.txt)")
class TestWeb(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._orig = (progreso.DIRECTORIO, progreso.PERFIL_ACTUAL)
        progreso.DIRECTORIO = self._dir
        from web.app import create_app
        self.app = create_app(token="secreto")
        self.c = self.app.test_client()
        self.h = {"X-Tortu-Token": "secreto"}
        progreso.guardar_config(progreso.cargar_progreso(), onboarding=True)   # sin pasar por la bienvenida

    def tearDown(self):
        progreso.DIRECTORIO, progreso.PERFIL_ACTUAL = self._orig
        shutil.rmtree(self._dir)

    def post(self, ruta, datos=None, **kw):
        return self.c.post(ruta, json=datos or {}, headers=self.h, **kw)

    # ── seguridad ──
    def test_api_sin_token_rechazada(self):
        self.assertEqual(self.c.post("/api/ejecutar", json={"codigo": "mostrar 1"}).status_code, 403)
        self.assertEqual(self.c.post("/api/ejecutar", json={}, headers={"X-Tortu-Token": "otro"}).status_code, 403)

    def test_host_ajeno_rechazado(self):
        r = self.c.get("/", headers={"Host": "malicioso.com"})
        self.assertEqual(r.status_code, 403)

    def test_cabeceras_de_seguridad_en_toda_respuesta(self):
        respuestas = {"página": self.c.get("/"), "api": self.c.get("/api/estado", headers=self.h),
                      "estático": self.c.get("/static/css/tortu.css"), "404": self.c.get("/no-existe"),
                      "403": self.c.post("/api/ejecutar", json={})}
        for nombre, r in respuestas.items():
            with self.subTest(nombre):
                self.assertIn("frame-ancestors 'none'", r.headers.get("Content-Security-Policy", ""))
                self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
                self.assertEqual(r.headers.get("Referrer-Policy"), "no-referrer")
                self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")
                self.assertIn("camera=()", r.headers.get("Permissions-Policy", ""))
            r.close()

    def test_la_csp_no_permite_scripts_inline_ni_eval_ni_nada_de_afuera(self):
        csp = dict(d.strip().split(" ", 1) for d in self.c.get("/").headers["Content-Security-Policy"].split(";"))
        self.assertEqual(csp["script-src"], "'self'")
        self.assertEqual(csp["default-src"], "'self'")
        self.assertEqual(csp["connect-src"], "'self'")
        self.assertEqual(csp["object-src"], "'none'")
        self.assertNotIn("http", " ".join(csp.values()))

    @staticmethod
    def _scripts_inline_ejecutables(html):
        return [cuerpo[:60] for atributos, cuerpo in re.findall(r"<script\b([^>]*)>(.*?)</script>", html, re.S)
                if "src=" not in atributos and 'type="application/json"' not in atributos]

    def test_ninguna_plantilla_ni_pagina_tiene_scripts_inline(self):
        """Con script-src 'self' un script inline no correría: tiene que ir en un .js o como dato JSON."""
        for plantilla in sorted((Path(__file__).resolve().parent.parent / "web/templates").glob("*.html")):
            with self.subTest(plantilla.name):
                self.assertEqual(self._scripts_inline_ejecutables(plantilla.read_text(encoding="utf-8")), [])
        for ruta in ("/", "/mapa", "/resumen", "/logros", "/liga", "/referencia", "/repaso", "/experimentar",
                     "/tortuga", "/proyectos", "/leccion/hola-mundo", "/ejercicios/1", "/practica", "/ayuda"):
            with self.subTest(ruta):
                r = self.c.get(ruta)
                self.assertIn(r.status_code, (200, 302))
                self.assertEqual(self._scripts_inline_ejecutables(r.get_data(as_text=True)), [])

    def test_la_configuracion_de_la_pagina_viaja_como_json(self):
        html = self.c.get("/").get_data(as_text=True)
        dato = re.search(r'<script type="application/json" id="tortu-config">(.*?)</script>', html, re.S).group(1)
        self.assertEqual(json.loads(dato)["token"], "secreto")
        self.assertIn("avisos", json.loads(dato))

    # ── errores ──
    def test_pagina_404_humana_con_cabeceras(self):
        r = self.c.get("/no-existe")
        html = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 404)
        self.assertIn("Esta página no existe", html)
        self.assertIn("Volver al inicio", html)
        self.assertNotIn("Not Found", html)
        self.assertIn("frame-ancestors", r.headers["Content-Security-Policy"])

    def test_error_de_la_api_en_json(self):
        r = self.c.get("/api/no-existe", headers=self.h)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.get_json()["error"], "Esta página no existe")
        self.assertEqual(self.c.post("/api/ejecutar", json={}).get_json()["error"], "Esto no se puede abrir desde acá")

    def _rutas_que_explotan(self):
        def explotar():
            raise RuntimeError("detalle interno /ruta/secreta")
        self.app.add_url_rule("/explota", "explota", explotar)
        self.app.add_url_rule("/api/explota", "api_explota", explotar)

    def test_error_interno_sin_trazas_y_con_codigo_en_el_log(self):
        self._rutas_que_explotan()
        with self.assertLogs("tortuscript.web", level="ERROR") as log:
            r = self.c.get("/explota")
        html = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 500)
        self.assertIn("Algo se rompió de nuestro lado", html)
        self.assertIn("Tu progreso sigue guardado", html)
        for filtrado in ("Traceback", "RuntimeError", "/ruta/secreta", "Internal Server Error"):
            self.assertNotIn(filtrado, html)
        codigo = re.search(r"<code>([0-9A-F]{6})</code>", html).group(1)
        self.assertIn(codigo, log.output[0])
        self.assertIn("RuntimeError", "\n".join(log.output))                      # la traza queda en el log
        with self.assertLogs("tortuscript.web", level="ERROR"):
            api = self.c.get("/api/explota", headers=self.h)
        self.assertEqual(api.status_code, 500)
        self.assertRegex(api.get_json()["codigo"], r"^[0-9A-F]{6}$")
        self.assertNotIn("secreta", api.get_data(as_text=True))

    def test_la_pagina_de_error_no_depende_del_progreso(self):
        self._rutas_que_explotan()
        original = progreso.cargar_progreso
        progreso.cargar_progreso = lambda *a, **k: (_ for _ in ()).throw(OSError("disco roto"))
        try:
            with self.assertLogs("tortuscript.web", level="ERROR"):
                r = self.c.get("/explota")
        finally:
            progreso.cargar_progreso = original
        self.assertEqual(r.status_code, 500)
        self.assertIn("Algo se rompió de nuestro lado", r.get_data(as_text=True))

    # ── exportar / importar ──
    def test_exportar_pide_token_y_no_lleva_campos_internos(self):
        self.assertEqual(self.c.get("/api/perfil/exportar").status_code, 403)
        r = self.c.get("/api/perfil/exportar", headers=self.h).get_json()
        self.assertRegex(r["archivo"], r"^tortuscript-default-\d{4}-\d{2}-\d{2}\.json$")
        self.assertEqual(r["datos"]["formato"], "tortuscript-progreso")
        self.assertNotIn("_perfil", r["datos"]["progreso"])

    def test_importar_crea_un_perfil_nuevo_sin_pisar_y_cambia_a_ese(self):
        p = progreso.cargar_progreso()
        p["xp_total"] = 123
        progreso.guardar_progreso(p)
        sobre = self.c.get("/api/perfil/exportar", headers=self.h).get_json()["datos"]
        p["xp_total"] = 7                                                      # el perfil original sigue su vida
        progreso.guardar_progreso(p)
        r = self.post("/api/perfil/importar", {"sobre": sobre}).get_json()
        self.assertTrue(r["ok"])
        self.assertEqual(r["actual"], "default_2")                              # "default" ya existía
        self.assertEqual(progreso.PERFIL_ACTUAL, "default_2")
        self.assertEqual(progreso.cargar_progreso("default_2")["xp_total"], 123)
        self.assertEqual(progreso.cargar_progreso("default")["xp_total"], 7)    # no se pisó
        self.assertEqual(r["estado"]["xp"], 123)

    def test_importar_rechaza_archivos_invalidos_o_enormes(self):
        r = self.post("/api/perfil/importar", {"sobre": {"formato": "otro"}})
        self.assertEqual(r.status_code, 400)
        self.assertIn("no es un progreso de TortuScript", r.get_json()["mensaje"])
        enorme = self.post("/api/perfil/importar", {"sobre": {"relleno": "x" * 1_100_000}})
        self.assertEqual(enorme.status_code, 400)
        self.assertIn("demasiado grande", enorme.get_json()["mensaje"])
        self.assertEqual(self.c.post("/api/perfil/importar", json={"sobre": {}}).status_code, 403)   # sin token
        self.assertEqual(progreso.obtener_perfiles(), ["default"])              # no se creó nada

    def test_el_modal_de_perfiles_ofrece_guardar_y_traer(self):
        html = self.c.get("/").get_data(as_text=True)
        for id_ in ("pf-exportar", "pf-importar", "pf-archivo"):
            self.assertIn(f'id="{id_}"', html)

    # ── ayuda ──
    def test_pagina_de_ayuda_en_el_menu_y_con_sus_preguntas(self):
        from tortuscript import contenido
        self.assertIn('href="/ayuda"', self.c.get("/").get_data(as_text=True))
        html = self.c.get("/ayuda").get_data(as_text=True)
        for p in contenido.cargar_ayuda()["preguntas"]:
            self.assertIn(p["pregunta"], html)
        self.assertIn("¿Cómo paso mi progreso a otra compu?", html)
        self.assertEqual(self._scripts_inline_ejecutables(html), [])

    def test_la_ayuda_esta_bien_formada_y_con_frases_cortas(self):
        from tortuscript import contenido
        from tortuscript.validacion import _revisar_texto
        ayuda = contenido.cargar_ayuda()
        self.assertTrue(ayuda["intro"])
        for p in ayuda["preguntas"]:
            self.assertTrue(p["icono"] and p["pregunta"].endswith("?") and p["respuesta"])
            hallazgos = []
            for parrafo in p["respuesta"]:
                _revisar_texto(parrafo, p["pregunta"], hallazgos)
            self.assertEqual([h.mensaje for h in hallazgos], [], p["pregunta"])     # mismas reglas que los cursos

    # ── dado ──
    def test_jugar_con_dado_devuelve_la_semilla_para_repetir_las_tiradas(self):
        codigo = "repetir 5 veces:\n    mostrar dado(1000)"
        r = self.post("/api/ejecutar", {"codigo": codigo}).get_json()
        self.assertIsInstance(r["semilla"], int)
        otra = self.post("/api/ejecutar", {"codigo": codigo, "semilla": r["semilla"]}).get_json()
        self.assertEqual(r["salida_programa"], otra["salida_programa"])

    # ── páginas ──
    def test_paginas(self):
        for ruta in ("/", "/experimentar", "/tortuga", "/ejercicios/1"):
            with self.subTest(ruta=ruta):
                r = self.c.get(ruta)
                self.assertEqual(r.status_code, 200)
                self.assertIn("secreto", r.get_data(as_text=True))   # token embebido
        self.assertEqual(self.c.get("/ejercicios/99").status_code, 404)

    def test_ejercicio_bloqueado_redirige(self):
        r = self.c.get("/ejercicios/5")
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/ejercicios/1"))

    # ── API ──
    def test_traducir(self):
        r = self.post("/api/traducir", {"codigo": 'y es 3\nmostrar y'}).get_json()
        self.assertEqual(r["python"], "y = 3\nprint(y)")

    def test_ciclo_de_preguntar(self):
        codigo = 'n es preguntar("¿Nombre? ")\nmostrar "Hola " + n'
        r1 = self.post("/api/ejecutar", {"codigo": codigo}).get_json()
        self.assertEqual(r1["pregunta"], "¿Nombre? ")
        r2 = self.post("/api/ejecutar", {"codigo": codigo, "entradas": ["Ana"]}).get_json()
        self.assertIsNone(r2["pregunta"])
        self.assertIn("Hola Ana", r2["salida"])

    def test_evaluar_correcto_guarda_premio(self):
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertEqual(r["premio"], {"estrellas": 3, "xp": 30, "mejora": True, "sube_nivel": False})
        self.assertEqual(r["estado_juego"]["xp"], 30)
        self.assertEqual(self.c.get("/ejercicios/2").status_code, 200)   # se desbloqueó

    def test_evaluar_incorrecto_no_desbloquea(self):
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "otra cosa"'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "incorrecto")
        self.assertNotIn("premio", r)
        self.assertEqual(self.post("/api/ejercicios/2/evaluar", {"codigo": "mostrar 1"}).status_code, 403)

    def test_pistas_restan_estrellas_y_se_reinician_al_abrir(self):
        self.c.get("/ejercicios/1")
        self.post("/api/ejercicios/1/pista")
        r = self.post("/api/ejercicios/1/pista").get_json()
        self.assertEqual(r["nivel"], 2)
        ev = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual(ev["premio"]["estrellas"], 1)                    # 2 pistas → 1 estrella
        self.c.get("/ejercicios/1")                                        # reabrir reinicia
        self.assertEqual(self.post("/api/ejercicios/1/pista").get_json()["nivel"], 1)

    def test_pista_3_muestra_solucion_y_python(self):
        for _ in range(3):
            r = self.post("/api/ejercicios/1/pista").get_json()
        self.assertEqual(r["codigo"], 'mostrar "Hola mundo"')
        self.assertEqual(r["python"], 'print("Hola mundo")')

    def test_error_se_explica(self):
        r = self.post("/api/ejecutar", {"codigo": "mostrar x"}).get_json()
        self.assertTrue(r["error"])
        self.assertIn("«x»", r["mensaje"])

    # ── mapa, resumen, referencia y repaso ──
    def _completar(self, *indices_estrellas):
        p = progreso.cargar_progreso()
        for i, e in indices_estrellas:
            progreso.registrar_ejercicio(p, i, e, {1: 5, 2: 20, 3: 30}[e])

    def test_paginas_nuevas(self):
        for ruta in ("/mapa", "/resumen", "/referencia", "/repaso"):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.c.get(ruta).status_code, 200)

    def test_mapa_refleja_progreso(self):
        self._completar((0, 3), (1, 1))
        html = self.c.get("/mapa").get_data(as_text=True)
        self.assertIn("NIVEL 1", html)
        self.assertIn("2/30", html)                      # ejercicios completados
        self.assertIn("ficha perfecto", html)
        self.assertIn("ficha intentado", html)
        self.assertIn("ficha bloqueada", html)           # los que aún no se desbloquean
        self.assertIn("¡Te toca!", html)                 # el siguiente pendiente
        self.assertIn('href="/leccion/', html)              # las fichas abren la lección

    def test_resumen_hoy(self):
        html = self.c.get("/resumen").get_data(as_text=True)
        self.assertIn("Todavía no completaste ningún ejercicio hoy", html)
        self.assertEqual(html.count('class="dia'), 7)
        self._completar((0, 3))
        html = self.c.get("/resumen").get_data(as_text=True)
        self.assertIn("1 día", html)
        self.assertIn("Ejercicios de hoy (1)", html)
        self.assertIn("Mostrar texto", html)

    def test_referencia_tiene_todo_y_escapa(self):
        html = self.c.get("/referencia").get_data(as_text=True)
        for texto in ("Mostrar en pantalla", "Preguntar", "Tortuga", "TortuScript", "Python"):
            self.assertIn(texto, html)
        self.assertNotIn("<script>alert", html)

    def test_repaso_sin_completados(self):
        r = self.c.get("/repaso/todos", follow_redirects=True)
        self.assertIn("No hay ejercicios para repasar", r.get_data(as_text=True))
        self.assertEqual(self.c.get("/repaso/inventado").status_code, 404)

    def test_repaso_recorre_la_cola(self):
        self._completar((0, 3), (1, 1), (2, 2))
        r = self.c.get("/repaso/dificiles?s=1")
        self.assertEqual(r.status_code, 302)
        html = self.c.get(r.headers["Location"]).get_data(as_text=True)
        self.assertIn("🔁 1/3", html)
        self.assertIn("Nivel 1", html)
        self.assertIn('href="/repaso/dificiles/2?s=1"', html)     # siguiente
        # El más difícil (1 estrella) es el ejercicio 2 → su consigna aparece primero
        self.assertIn("2. Texto o cuenta", html)
        ultimo = self.c.get("/repaso/dificiles/3?s=1").get_data(as_text=True)
        self.assertIn("Terminar repaso", ultimo)
        fin = self.c.get("/repaso/dificiles/4?s=1").get_data(as_text=True)
        self.assertIn("¡Terminaste el repaso!", fin)

    def test_repaso_conserva_la_cola_si_mejoran_las_estrellas(self):
        self._completar((0, 1), (1, 1))
        self.c.get("/repaso/imperfectos?s=5")
        self._completar((0, 3))                                   # a mitad del repaso pasa a 3 estrellas
        html = self.c.get("/repaso/imperfectos/2?s=5").get_data(as_text=True)
        self.assertIn("🔁 2/2", html)                             # la cola no se achicó

    def test_ejercicio_de_repaso_se_puede_evaluar(self):
        self._completar((0, 1))
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertEqual(r["premio"]["estrellas"], 3)
        self.assertTrue(r["premio"]["mejora"])

    # ── motor de lecciones ──
    def comprobar(self, i, respuesta, leccion="hola-mundo"):
        return self.post(f"/api/lecciones/{leccion}/pasos/{i}/comprobar", {"respuesta": respuesta})

    def test_pagina_de_leccion_no_filtra_respuestas(self):
        html = self.c.get("/leccion/hola-mundo").get_data(as_text=True)
        self.assertIn("datos-leccion", html)
        self.assertIn("Hola mundo", html)
        self.assertNotIn('"correcta"', html)
        self.assertNotIn('"solucion"', html)
        self.assertEqual(self.c.get("/leccion/no-existe").status_code, 404)

    def test_leccion_bloqueada_redirige(self):
        r = self.c.get("/leccion/texto-o-cuenta")
        self.assertEqual(r.status_code, 302)
        self._completar((0, 3))                                  # el ejercicio 1 ya hecho → lección 1 completa
        self.assertEqual(self.c.get("/leccion/texto-o-cuenta").status_code, 200)

    def test_paso_incorrecto_da_pista_y_luego_permite_ver_respuesta(self):
        self.assertEqual(self.post("/api/lecciones/hola-mundo/pasos/1/respuesta").status_code, 403)   # sin intentar
        r = self.comprobar(1, "escribir").get_json()
        self.assertFalse(r["ok"])
        self.assertIn("orden del ejemplo", r["pista"])
        self.assertFalse(r["puede_ver_respuesta"])
        self.assertTrue(self.comprobar(1, "pantalla").get_json()["puede_ver_respuesta"])
        r = self.post("/api/lecciones/hola-mundo/pasos/1/respuesta").get_json()
        self.assertEqual(r["respuesta"], "mostrar")
        p = progreso.cargar_progreso()
        paso = p["lecciones"]["hola-mundo"]["pasos"]["1"]
        self.assertEqual((paso["xp"], paso["perfecto"]), (0, False))
        self.assertIn("fecha", paso)                                                        # desde acá parte la práctica del día

    def test_leccion_completa_paso_a_paso(self):
        r = self.comprobar(0, True).get_json()                                     # explicación
        self.assertTrue(r["ok"])
        self.assertEqual(r["xp"], 0)
        self.assertEqual(self.comprobar(1, "mostrar").get_json()["xp"], 5)         # elegir, 1.er intento
        self.comprobar(2, ["sumar"])                                               # completar: mal
        self.assertEqual(self.comprobar(2, ["mostrar"]).get_json()["xp"], 2)        # con reintento
        malo = self.comprobar(3, ['mostrar "Chau"', 'mostrar "Hola"']).get_json()
        self.assertEqual(malo["malos"], [0, 1])
        self.assertTrue(self.comprobar(3, ['mostrar "Hola"', 'mostrar "Chau"']).get_json()["ok"])
        self.assertTrue(self.comprobar(4, "Buen día").get_json()["ok"])
        # el último paso es 'escribir': se evalúa ejecutando y completa la lección
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertTrue(r["leccion"]["completa"])
        self.assertTrue(r["leccion"]["recien_completa"])
        self.assertFalse(r["leccion"]["perfecta"])                                 # hubo un reintento
        self.assertEqual(r["leccion"]["siguiente"], "texto-o-cuenta")
        p = progreso.cargar_progreso()
        self.assertEqual(p["xp_total"], 5 + 2 + 2 + 5 + 30)                        # elegir, completar, ordenar, predecir + ejercicio

    def test_escribir_no_se_comprueba_por_la_api_de_pasos(self):
        self.assertEqual(self.comprobar(5, "x").status_code, 400)
        self.assertEqual(self.comprobar(99, "x").status_code, 404)

    def test_perfecta_si_todo_al_primer_intento(self):
        self.comprobar(0, True); self.comprobar(1, "mostrar"); self.comprobar(2, ["mostrar"])
        self.comprobar(3, ['mostrar "Hola"', 'mostrar "Chau"']); self.comprobar(4, "Buen día")
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertTrue(r["leccion"]["perfecta"])

    def test_la_pagina_de_ejercicio_ofrece_la_leccion_completa(self):
        self.assertIn("Hacé la lección completa", self.c.get("/ejercicios/1").get_data(as_text=True))
        self._completar((0, 3))
        self.assertIn("Hacé la lección completa", self.c.get("/ejercicios/2").get_data(as_text=True))
        self.assertNotIn("Hacé la lección completa", self.c.get("/repaso/todos/1?s=1", follow_redirects=True).get_data(as_text=True))

    # ── evaluar y pistas por paso de lección (también sirven a los ejercicios clásicos) ──
    def test_evaluar_paso_escribir_de_una_leccion(self):
        r = self.post("/api/lecciones/hola-mundo/pasos/5/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertEqual((r["premio"]["estrellas"], r["premio"]["xp"], r["premio"]["mejora"]), (3, 30, True))
        p = progreso.cargar_progreso()
        self.assertTrue(p["ejercicios"]["0"]["completado"])                    # clave histórica intacta
        self.assertIn("5", p["lecciones"]["hola-mundo"]["pasos"])
        self.assertEqual(self.post("/api/lecciones/hola-mundo/pasos/1/evaluar", {"codigo": "x"}).status_code, 400)
        self.assertEqual(self.post("/api/lecciones/hola-mundo/pasos/99/evaluar", {}).status_code, 404)
        self.assertEqual(self.post("/api/lecciones/no-existe/pasos/0/evaluar", {}).status_code, 404)

    def test_pistas_por_paso_bajan_las_estrellas_y_no_se_mezclan_con_otra_leccion(self):
        for esperado in (1, 2, 3):
            r = self.post("/api/lecciones/hola-mundo/pasos/5/pista").get_json()
            self.assertEqual(r["nivel"], esperado)
        self.assertEqual(r["codigo"], 'mostrar "Hola mundo"')
        r = self.post("/api/lecciones/hola-mundo/pasos/5/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual((r["premio"]["estrellas"], r["premio"]["xp"]), (1, 5))
        self._completar((0, 3), (1, 3))
        self.assertEqual(self.post("/api/lecciones/texto-o-cuenta/pasos/5/pista").get_json()["nivel"], 1)   # empieza de cero

    def test_abrir_la_leccion_reinicia_las_pistas(self):
        self.post("/api/lecciones/hola-mundo/pasos/5/pista")
        self.c.get("/leccion/hola-mundo")
        self.assertEqual(self.post("/api/lecciones/hola-mundo/pasos/5/pista").get_json()["nivel"], 1)

    def test_api_de_pasos_respeta_el_bloqueo(self):
        self.assertEqual(self.post("/api/lecciones/texto-o-cuenta/pasos/0/comprobar", {"respuesta": True}).status_code, 403)
        self.assertEqual(self.post("/api/lecciones/texto-o-cuenta/pasos/5/evaluar", {"codigo": "x"}).status_code, 403)

    def test_los_ejercicios_clasicos_siguen_funcionando_y_comparten_pistas(self):
        self.post("/api/ejercicios/1/pista")
        self.post("/api/ejercicios/1/pista")
        r = self.post("/api/ejercicios/1/evaluar", {"codigo": 'mostrar "Hola mundo"'}).get_json()
        self.assertEqual((r["premio"]["estrellas"], r["premio"]["xp"]), (1, 10))          # 2 pistas vistas
        self.assertEqual(r["leccion"]["siguiente"], "texto-o-cuenta")
        self.assertEqual(self.post("/api/ejercicios/2/evaluar", {"codigo": "mostrar 1"}).status_code, 200)   # desbloqueado por el 1

    def test_api_tortuga(self):
        r = self.post("/api/tortuga", {"codigo": "avanzar 10\ngirar_der 90"}).get_json()
        self.assertEqual([o["o"] for o in r["ordenes"]], ["avanzar", "girar_der"])
        self.assertEqual(self.c.post("/api/tortuga", json={}).status_code, 403)

    def test_perfiles(self):
        r = self.post("/api/perfil", {"nombre": "../../Lua"}).get_json()
        self.assertEqual(r["actual"], "lua")
        self.assertEqual(self.post("/api/perfil", {"nombre": "///"}).status_code, 400)
        self.assertIn("lua", self.c.get("/api/perfiles", headers=self.h).get_json()["perfiles"])


if __name__ == "__main__":
    unittest.main()
