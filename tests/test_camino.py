"""Camino de lecciones, onboarding y meta diaria."""
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tortuscript import contenido, leccion, liga, logros, progreso

try:
    import flask  # noqa: F401
    HAY_FLASK = True
except ImportError:
    HAY_FLASK = False


class Base(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._orig = (progreso.DIRECTORIO, progreso.PERFIL_ACTUAL)
        progreso.DIRECTORIO = self._dir
        progreso.PERFIL_ACTUAL = "default"

    def tearDown(self):
        progreso.DIRECTORIO, progreso.PERFIL_ACTUAL = self._orig
        shutil.rmtree(self._dir)


class TestMetaDiaria(Base):
    def test_xp_del_dia_y_total(self):
        p = progreso.cargar_progreso()
        progreso.sumar_xp(p, 10, date(2026, 9, 25))
        progreso.sumar_xp(p, 5, date(2026, 9, 25))
        progreso.sumar_xp(p, 7, date(2026, 9, 26))
        progreso.sumar_xp(p, 0, date(2026, 9, 26))
        progreso.sumar_xp(p, -3, date(2026, 9, 26))
        self.assertEqual(p["xp_total"], 22)
        self.assertEqual(progreso.xp_de_hoy(p, date(2026, 9, 25)), 15)
        self.assertEqual(progreso.xp_de_hoy(p, date(2026, 9, 26)), 7)
        self.assertEqual(progreso.xp_de_hoy(p, date(2026, 9, 27)), 0)

    def test_solo_se_guardan_30_dias(self):
        p = progreso.cargar_progreso()
        for d in range(1, 29):
            progreso.sumar_xp(p, 1, date(2026, 8, d))
        for d in range(1, 11):
            progreso.sumar_xp(p, 1, date(2026, 9, d))
        self.assertEqual(len(p["xp_por_dia"]), 30)
        self.assertNotIn("2026-08-01", p["xp_por_dia"])

    def test_los_ejercicios_y_pasos_suman_al_dia(self):
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        progreso.registrar_paso_leccion(p, "l", 0, 5, True, 2)
        self.assertEqual(progreso.xp_de_hoy(p), 35)
        self.assertEqual(p["xp_total"], 35)

    def test_meta_en_xp(self):
        p = progreso.cargar_progreso()
        self.assertEqual(progreso.meta_diaria_xp(p), 40)
        for minutos, xp in ((5, 20), (10, 40), (15, 60)):
            self.assertTrue(progreso.guardar_config(p, meta_min=minutos))
            self.assertEqual(progreso.meta_diaria_xp(p), xp)

    def test_config_invalida_se_rechaza(self):
        p = progreso.cargar_progreso()
        self.assertFalse(progreso.guardar_config(p, meta_min=7))
        self.assertFalse(progreso.guardar_config(p, experiencia="experto"))
        self.assertEqual(p["config"]["meta_min"], 10)


class TestOnboarding(Base):
    def test_perfil_nuevo_necesita_bienvenida(self):
        self.assertTrue(progreso.necesita_onboarding(progreso.cargar_progreso()))

    def test_con_progreso_previo_no_hace_falta(self):
        (self._dir / "progreso_default.json").write_text(
            '{"version": 2, "xp_total": 30, "ejercicios": {"0": {"completado": true, "estrellas": 3, "xp": 30}}}',
            encoding="utf-8")
        self.assertFalse(progreso.necesita_onboarding(progreso.cargar_progreso()))

    def test_una_vez_hecha_no_se_repite_y_persiste(self):
        p = progreso.cargar_progreso()
        progreso.guardar_config(p, experiencia="poquito", meta_min=15, nombre="Lua", onboarding=True)
        again = progreso.cargar_progreso()
        self.assertFalse(progreso.necesita_onboarding(again))
        self.assertEqual((again["config"]["experiencia"], again["config"]["meta_min"], again["config"]["nombre"]),
                         ("poquito", 15, "Lua"))

    def test_config_de_version_anterior_a_medias_se_completa(self):
        (self._dir / "progreso_default.json").write_text(
            '{"version": 3, "xp_total": 0, "ejercicios": {}, "config": {"meta_min": 5}}', encoding="utf-8")
        cfg = progreso.cargar_progreso()["config"]
        self.assertEqual((cfg["meta_min"], cfg["onboarding"], cfg["experiencia"]), (5, False, None))


class TestEstadoCamino(unittest.TestCase):
    def setUp(self):
        self.curso = contenido.cargar_curso()
        self.indices = {}
        for i, e in enumerate(contenido.ejercicios()):
            self.indices.setdefault(e["leccion_id"], []).append(i)

    def planas(self, p):
        return [l for s in leccion.estado_camino(self.curso, p, self.indices) for l in s["lecciones"]]

    def test_progreso_vacio_la_primera_es_la_actual(self):
        estados = [l["estado"] for l in self.planas({})]
        self.assertEqual(estados[0], "actual")
        self.assertTrue(all(e == "bloqueada" for e in estados[1:]))
        self.assertEqual(len(estados), 30)

    def test_ejercicios_viejos_completados_cuentan_como_lecciones(self):
        p = {"ejercicios": {"0": {"completado": True, "estrellas": 3},
                            "1": {"completado": True, "estrellas": 1}}}
        planas = self.planas(p)
        # con su 'escribir' hecho, la lección cuenta como completada; perfecta solo si la hizo el motor
        self.assertEqual([l["estado"] for l in planas[:3]], ["hecha", "hecha", "actual"])
        p["ejercicios"]["1"]["estrellas"] = 3
        self.assertEqual(self.planas(p)[1]["estado"], "hecha")

    def test_leccion_de_un_solo_paso_escribir_con_3_estrellas_es_perfecta(self):
        curso = {"secciones": [{"nivel": 1, "titulo": "T", "lecciones": [
            {"id": "x", "titulo": "1. Uno", "pasos": [{"tipo": "escribir"}]}]}]}
        p = {"ejercicios": {"0": {"completado": True, "estrellas": 3}}}
        self.assertEqual(leccion.estado_camino(curso, p, {"x": [0]})[0]["lecciones"][0]["estado"], "perfecta")

    def test_perfecta_desde_el_motor(self):
        p = {"lecciones": {"hola-mundo": {"completada": True, "perfecta": True}}}
        self.assertEqual(self.planas(p)[0]["estado"], "perfecta")

    def test_numero_nombre_y_pasos(self):
        primera = self.planas({})[0]
        self.assertEqual((primera["numero"], primera["nombre"], primera["pasos"]), ("1", "Hola mundo", 6))


@unittest.skipUnless(HAY_FLASK, "Flask no instalado")
class TestWebCamino(Base):
    def setUp(self):
        super().setUp()
        from web.app import create_app
        self.app = create_app(token="t")
        self.c = self.app.test_client()
        self.h = {"X-Tortu-Token": "t"}

    def post(self, ruta, datos=None):
        return self.c.post(ruta, json=datos or {}, headers=self.h)

    def test_perfil_nuevo_va_a_la_bienvenida(self):
        for ruta in ("/", "/aprender", "/mapa", "/referencia", "/tortuga"):
            with self.subTest(ruta=ruta):
                r = self.c.get(ruta)
                self.assertEqual(r.status_code, 302)
                self.assertTrue(r.headers["Location"].endswith("/bienvenida"))
        self.assertEqual(self.c.get("/bienvenida").status_code, 200)
        with self.c.get("/static/css/tortu.css") as css:
            self.assertEqual(css.status_code, 200)                                  # sin redirigir
        self.assertEqual(self.post("/api/traducir", {"codigo": "mostrar 1"}).status_code, 200)

    def test_onboarding_completo(self):
        r = self.post("/api/onboarding", {"nombre": "Lua Pérez", "experiencia": "nunca", "meta_min": 15}).get_json()
        self.assertTrue(r["ok"])
        self.assertEqual(r["actual"], "lua_pérez")
        self.assertEqual(r["estado"]["meta_xp"], 60)
        self.assertEqual(r["estado"]["nombre"], "Lua Pérez")
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("¡Hola, Lua Pérez!", html)
        self.assertIn("Meta de hoy", html)
        self.assertEqual(self.c.get("/bienvenida").status_code, 200)              # se puede volver a ver

    def test_onboarding_sin_nombre_usa_el_perfil_actual(self):
        r = self.post("/api/onboarding", {"nombre": "", "experiencia": "bastante", "meta_min": 5}).get_json()
        self.assertEqual(r["actual"], "default")
        self.assertEqual(self.c.get("/").status_code, 200)

    def test_onboarding_rechaza_valores_invalidos(self):
        self.assertEqual(self.post("/api/onboarding", {"nombre": "///", "meta_min": 10}).status_code, 400)
        self.assertEqual(self.post("/api/onboarding", {"experiencia": "genio", "meta_min": 10}).status_code, 400)
        self.assertEqual(self.post("/api/onboarding", {"meta_min": 99}).status_code, 400)
        self.assertEqual(self.c.get("/").status_code, 302)                        # sigue sin hacerse

    def test_api_config(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self.assertEqual(self.post("/api/config", {"meta_min": 5}).get_json()["estado"]["meta_xp"], 20)
        self.assertEqual(self.post("/api/config", {"meta_min": 8}).status_code, 400)
        self.assertEqual(self.c.post("/api/config", json={"meta_min": 5}).status_code, 403)   # sin token

    def test_camino_en_el_inicio(self):
        self.post("/api/onboarding", {"meta_min": 10})
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("Camino de lecciones", html)
        self.assertEqual(html.count('class="parada'), 30)
        self.assertIn("¡Te toca!", html)
        self.assertIn('href="/leccion/hola-mundo"', html)
        self.assertIn("0/54", html)

    def test_aprender_lleva_a_la_leccion_actual(self):
        self.post("/api/onboarding", {"meta_min": 10})
        r = self.c.get("/aprender")
        self.assertTrue(r.headers["Location"].endswith("/leccion/hola-mundo"))
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        self.assertTrue(self.c.get("/aprender").headers["Location"].endswith("/leccion/texto-o-cuenta"))

    # ── curso de la tortuga ──
    def _terminar_hasta(self, leccion_id):
        """Da por completada (con el formato del motor) cada lección del curso 1 hasta `leccion_id` inclusive."""
        curso = contenido.cargar_curso()
        p = progreso.cargar_progreso()
        for lec in leccion.lista_lecciones(curso):
            progreso.registrar_paso_leccion(p, lec["id"], 0, 0, True, 1)
            if lec["id"] == leccion_id:
                break

    def _dar_por_completa(self, leccion_id):
        progreso.registrar_paso_leccion(progreso.cargar_progreso(), leccion_id, 0, 0, True, 1)

    def _abrir_laberintos(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("dos-variables")
        for _, lec in contenido.lecciones(contenido.cargar_curso("tortuga")):
            if lec["id"].startswith("laberinto"):
                break
            self._dar_por_completa(lec["id"])

    def test_el_laberinto_llega_con_paredes_y_sin_dibujo_objetivo_ni_solucion(self):
        self._abrir_laberintos()
        html = self.c.get("/leccion/laberinto-1").get_data(as_text=True)
        self.assertIn('"laberinto"', html)
        self.assertIn('"paredes"', html)
        self.assertNotIn('"objetivo"', html)
        self.assertNotIn('"solucion"', html)

    def test_evaluar_el_laberinto_por_reglas(self):
        self._abrir_laberintos()
        ruta = "/api/lecciones/laberinto-1/pasos/2/evaluar"
        choque = self.post(ruta, {"codigo": "avanzar 100\ngirar_izq 90\navanzar 100"}).get_json()
        self.assertEqual((choque["evaluacion"]["estado"], choque["evaluacion"]["linea"]), ("choque", 3))
        self.assertNotIn("premio", choque)
        lejos = self.post(ruta, {"codigo": "avanzar 50"}).get_json()
        self.assertEqual(lejos["evaluacion"]["estado"], "no_llega")
        ok = self.post(ruta, {"codigo": "avanzar 110\ngirar_der 90\navanzar 100\ngirar_izq 90\navanzar 90"}).get_json()
        self.assertEqual(ok["evaluacion"]["estado"], "correcto")                 # otra ruta, no la oficial
        self.assertEqual(ok["premio"]["estrellas"], 3)

    def test_el_ultimo_laberinto_exige_repetir(self):
        self._abrir_laberintos()
        self._dar_por_completa("laberinto-1")
        self._dar_por_completa("laberinto-2")
        ruta = "/api/lecciones/laberinto-3/pasos/2/evaluar"
        a_mano = "\n".join(["avanzar 80\ngirar_der 90\navanzar 80\ngirar_izq 90"] * 4 + ["avanzar 80"])
        self.assertEqual(self.post(ruta, {"codigo": a_mano}).get_json()["evaluacion"]["estado"], "falta_usar")
        con_repetir = "repetir 4 veces:\n    avanzar 80\n    girar_der 90\n    avanzar 80\n    girar_izq 90\navanzar 80"
        self.assertEqual(self.post(ruta, {"codigo": con_repetir}).get_json()["evaluacion"]["estado"], "correcto")

    def test_la_tortuga_cambia_de_color_al_subir_de_nivel(self):
        self.post("/api/onboarding", {"meta_min": 10})
        html = self.c.get("/tortuga").get_data(as_text=True)
        self.assertIn(f'data-color-tortuga="{progreso.color_tortuga(1)}"', html)
        p = progreso.cargar_progreso()
        p["xp_total"] = progreso.UMBRALES_NIVEL[2]                                  # nivel 3
        progreso.guardar_progreso(p)
        html = self.c.get("/tortuga").get_data(as_text=True)
        self.assertIn(f'data-color-tortuga="{progreso.color_tortuga(3)}"', html)
        r = self.post("/api/tortuga", {"codigo": "avanzar 10"}).get_json()
        self.assertEqual([o["o"] for o in r["ordenes"]], ["avanzar"])             # el nivel no le cambia el color al lápiz
        paso = self.post("/api/lecciones/hola-mundo/pasos/0/comprobar", {}).get_json()
        self.assertEqual(paso["estado_juego"]["color_tortuga"], progreso.color_tortuga(3))

    def test_al_volver_otro_dia_el_inicio_cuenta_que_paso_y_que_sigue(self):
        self.post("/api/onboarding", {"meta_min": 10, "nombre": "Lua"})
        html = self.c.get("/").get_data(as_text=True)
        self.assertNotIn("Hola de nuevo", html)                                # perfil nuevo: saludo normal
        self._dar_por_completa("hola-mundo")                                    # ya había hecho una lección
        p = progreso.cargar_progreso()
        ayer = (date.today() - timedelta(days=1)).isoformat()
        p["ultimo_dia"], p["xp_por_dia"] = ayer, {ayer: 35}
        progreso.guardar_progreso(p)
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("¡Hola de nuevo, Lua!", html)
        self.assertIn("Ayer", html)
        self.assertIn("35 XP", html)
        self.assertIn("Hoy te espera <b>«", html)
        self.assertIn("▶ Continuar:", html)
        p["ultimo_dia"] = date.today().isoformat()                                  # ya vino hoy: no se repite
        progreso.guardar_progreso(p)
        self.assertNotIn("Hola de nuevo", self.c.get("/").get_data(as_text=True))

    def test_el_cierre_de_la_leccion_cuenta_que_aprendio_y_que_sigue(self):
        self.post("/api/onboarding", {"meta_min": 10})
        r = self.post("/api/lecciones/hola-mundo/pasos/0/comprobar", {}).get_json()
        self.assertEqual(r["leccion"]["aprendiste"], ["mostrar"])
        self.assertEqual(r["leccion"]["practicaste"], [])
        self.assertEqual(r["leccion"]["siguiente"], "texto-o-cuenta")

    def test_el_curso_de_la_tortuga_empieza_cerrado_y_se_abre_al_terminar_dos_variables(self):
        self.post("/api/onboarding", {"meta_min": 10})
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("Dibujá con la tortuga", html)
        self.assertIn("Se desbloquea al terminar «Dos variables»", html)
        self.assertIn("Se desbloquea al terminar «Desafío final»", html)            # el curso de Python
        self.assertEqual(self.c.get("/leccion/tortuga-avanzar").status_code, 302)          # bloqueada
        self._terminar_hasta("dos-variables")
        html = self.c.get("/").get_data(as_text=True)
        self.assertNotIn("Se desbloquea al terminar «Dos variables»", html)
        self.assertIn("Se desbloquea al terminar «Desafío final»", html)            # el de Python sigue cerrado
        self.assertEqual(self.c.get("/leccion/tortuga-avanzar").status_code, 200)
        self.assertEqual(self.c.get("/leccion/py-print").status_code, 302)

    def test_pagina_de_leccion_de_tortuga_trae_el_dibujo_objetivo_sin_la_solucion(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("dos-variables")
        self._dar_por_completa("tortuga-avanzar")
        html = self.c.get("/leccion/tortuga-girar").get_data(as_text=True)
        self.assertIn('"objetivo"', html)
        self.assertIn('"tortuga": true', html)
        self.assertNotIn('"solucion"', html)
        self.assertNotIn('"respuesta"', html)

    def test_evaluar_un_dibujo_da_xp_por_estrellas_y_se_recuerda_el_mejor(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("dos-variables")
        ruta = "/api/lecciones/tortuga-avanzar/pasos/4/evaluar"
        mal = self.post(ruta, {"codigo": "avanzar 50"}).get_json()
        self.assertEqual(mal["evaluacion"]["estado"], "incorrecto")
        self.assertNotIn("objetivo", mal["evaluacion"])
        self.assertEqual(self.post(ruta, {"codigo": "girar_der 90"}).get_json()["evaluacion"]["estado"], "sin_dibujo")
        self.assertEqual(len(mal["ordenes"]), 1)
        antes = progreso.cargar_progreso()["xp_total"]
        ok = self.post(ruta, {"codigo": "avanzar 60\navanzar 60"}).get_json()            # otra forma de dibujar lo mismo
        self.assertEqual(ok["evaluacion"]["estado"], "correcto")
        self.assertEqual((ok["premio"]["estrellas"], ok["premio"]["xp"], ok["premio"]["mejora"]), (3, 30, True))
        self.assertEqual(progreso.cargar_progreso()["xp_total"], antes + 30)
        p = progreso.cargar_progreso()
        self.assertEqual(p["lecciones"]["tortuga-avanzar"]["pasos"]["4"]["estrellas"], 3)
        self.assertNotIn("4", p["ejercicios"])                                              # no toca la clave de ejercicios
        repetido = self.post(ruta, {"codigo": "avanzar 120"}).get_json()
        self.assertFalse(repetido["premio"]["mejora"])                                       # sin XP doble
        self.assertEqual(progreso.cargar_progreso()["xp_total"], antes + 30)

    def test_pasos_de_dibujo_de_completar_y_ordenar_por_la_api(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("dos-variables")
        self._dar_por_completa("tortuga-avanzar")
        r = self.post("/api/lecciones/tortuga-girar/pasos/3/comprobar", {"respuesta": ["45"]}).get_json()
        self.assertFalse(r["ok"])
        self.assertEqual(r["malos"], [0])
        self.assertTrue(self.post("/api/lecciones/tortuga-girar/pasos/3/comprobar", {"respuesta": ["90"]}).get_json()["ok"])
        r = self.post("/api/lecciones/tortuga-girar/pasos/4/comprobar",
                      {"respuesta": ["avanzar 100", "girar_izq 90", "avanzar 100"]}).get_json()
        self.assertTrue(r["ok"])

    # ── gamificación en la web ──
    def _paso(self, i, respuesta, leccion_id="hola-mundo"):
        return self.post(f"/api/lecciones/{leccion_id}/pasos/{i}/comprobar", {"respuesta": respuesta}).get_json()

    def test_los_logros_llegan_como_avisos_una_sola_vez(self):
        self.post("/api/onboarding", {"meta_min": 10})
        r = self._paso(0, True)
        self.assertEqual([a["id"] for a in r["avisos"] if a["tipo"] == "logro"], ["primer-paso"])
        self.assertEqual(r["avisos"][0]["titulo"], "Primer paso")
        self.assertEqual(self._paso(1, "mostrar")["avisos"], [])
        html = self.c.get("/logros").get_data(as_text=True)
        self.assertIn("Primer paso", html)
        self.assertIn("Ganado el", html)
        self.assertEqual(progreso.cargar_progreso()["avisos"], [])

    def test_la_meta_diaria_se_avisa_al_cumplirla(self):
        self.post("/api/onboarding", {"meta_min": 5})                      # 20 XP
        for i, resp in ((1, "mostrar"), (2, ["mostrar"]), (3, ['mostrar "Hola"', 'mostrar "Chau"'])):
            self.assertNotIn("meta_cumplida", [a["tipo"] for a in self._paso(i, resp)["avisos"]])
        r = self._paso(4, "Buen día")
        self.assertIn("meta_cumplida", [a["tipo"] for a in r["avisos"]])
        self.assertEqual(r["estado_juego"]["meta_pct"], 100)
        self.assertIn("meta-diaria", progreso.cargar_progreso()["logros"])

    def test_estado_y_paginas_de_gamificacion(self):
        self.post("/api/onboarding", {"meta_min": 10})
        est = self.c.get("/api/estado", headers=self.h).get_json()
        self.assertEqual((est["congeladores"], est["reto_dias"], est["reto_total"]), (0, 0, 7))
        self.assertEqual((est["logros_ganados"], est["logros_total"]), (0, len(logros.LOGROS)))
        self.assertEqual((est["liga"]["liga"], est["liga"]["tamano"]), ("Bronce", 5))
        for ruta in ("/logros", "/liga", "/resumen", "/"):
            self.assertEqual(self.c.get(ruta).status_code, 200)
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("Reto de 7 días", html)
        self.assertIn("Liga Bronce", html)
        self.assertIn('<details class="mas">', html)                                    # menú "Más"

    def test_liga_con_otro_perfil_de_la_pc(self):
        self.post("/api/onboarding", {"meta_min": 10, "nombre": "Lua"})
        p = progreso.cargar_progreso("tomi")
        p["config"]["nombre"] = "Tomi"
        progreso.sumar_xp(p, 500)
        progreso.guardar_progreso(p)
        html = self.c.get("/liga").get_data(as_text=True)
        self.assertIn("Tomi", html)
        self.assertIn("(vos)", html)
        self.assertEqual(html.count('class="puesto"'), 5)                               # el grupo se completa con rivales

    def test_al_cambiar_de_semana_se_sube_de_liga_y_se_avisa_en_la_pagina(self):
        from datetime import date, timedelta
        self.post("/api/onboarding", {"meta_min": 10})
        hoy = date.today()
        anterior = liga.lunes_de(hoy) - timedelta(days=2)                              # un sábado de la semana pasada
        p = progreso.cargar_progreso()
        p["liga"] = {"nivel": 0, "semana": liga.clave_semana(anterior)}
        p["xp_por_dia"] = {str(anterior): 900}
        progreso.guardar_progreso(p)
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("liga_asciende", html)
        self.assertIn("Plata", html)
        self.assertEqual(progreso.cargar_progreso()["liga"], {"nivel": 1, "semana": liga.clave_semana(hoy)})
        self.assertNotIn("liga_asciende", self.c.get("/").get_data(as_text=True))       # el aviso se cuenta una sola vez

    # ── práctica del día ──
    def _con_pasos_viejos(self):
        """hola-mundo con sus 4 pasos rápidos hechos hace una semana."""
        self.post("/api/onboarding", {"meta_min": 10})
        p = progreso.cargar_progreso()
        for i in (1, 2, 3, 4):
            progreso.registrar_paso_leccion(p, "hola-mundo", i, 5, True, 6)
            p["lecciones"]["hola-mundo"]["pasos"][str(i)]["fecha"] = "2026-01-01"
        progreso.guardar_progreso(p)

    def _practica(self, i, respuesta):
        return self.post("/api/practica/comprobar", {"leccion": "hola-mundo", "paso": i, "respuesta": respuesta}).get_json()

    def test_sin_nada_para_repasar_se_dice_que_esta_al_dia(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self.assertIn("¡Estás al día!", self.c.get("/practica").get_data(as_text=True))
        est = self.c.get("/api/estado", headers=self.h).get_json()
        self.assertEqual(est["practica_pendientes"], 0)
        self.assertIn("¡Estás al día! Volvé mañana.", self.c.get("/").get_data(as_text=True))

    def test_la_practica_lista_las_tarjetas_vencidas_sin_filtrar_respuestas(self):
        self._con_pasos_viejos()
        self.assertEqual(self.c.get("/api/estado", headers=self.h).get_json()["practica_pendientes"], 4)
        html = self.c.get("/practica").get_data(as_text=True)
        self.assertIn('"modo": "practica"', html)
        self.assertIn("Práctica del día", html)
        self.assertNotIn('"correcta"', html)
        self.assertNotIn('"respuesta"', html)
        self.assertIn('"leccion": "hola-mundo"', html)

    def test_acertar_sube_la_tarjeta_da_xp_y_la_saca_de_las_pendientes(self):
        self._con_pasos_viejos()
        self.c.get("/practica")
        antes = progreso.cargar_progreso()["xp_total"]
        r = self._practica(1, "mostrar")
        self.assertEqual((r["ok"], r["xp"], r["perfecto"]), (True, 2, True))
        p = progreso.cargar_progreso()
        self.assertEqual(p["xp_total"], antes + 2)
        self.assertEqual(p["repaso"]["hola-mundo:1"]["caja"], 1)
        self.assertEqual(self.c.get("/api/estado", headers=self.h).get_json()["practica_pendientes"], 3)

    def test_errar_pide_pista_y_el_acierto_posterior_no_da_xp_ni_sube_de_caja(self):
        self._con_pasos_viejos()
        self.c.get("/practica")
        r = self._practica(1, "escribir")
        self.assertFalse(r["ok"])
        self.assertTrue(r["pista"])
        self.assertFalse(r["puede_ver_respuesta"])
        r = self._practica(1, "mostrar")
        self.assertEqual((r["ok"], r["xp"], r["perfecto"]), (True, 0, False))
        self.assertEqual(progreso.cargar_progreso()["repaso"]["hola-mundo:1"]["fallos"], 1)

    def test_ver_la_respuesta_de_una_tarjeta_solo_tras_dos_errores(self):
        self._con_pasos_viejos()
        self.c.get("/practica")
        pedir = lambda: self.post("/api/practica/respuesta", {"leccion": "hola-mundo", "paso": 1})   # noqa: E731
        self.assertEqual(pedir().status_code, 403)
        self._practica(1, "pantalla"); self._practica(1, "escribir")
        r = pedir().get_json()
        self.assertEqual(r["respuesta"], "mostrar")
        self.assertEqual(progreso.cargar_progreso()["repaso"]["hola-mundo:1"]["fallos"], 1)

    def test_solo_se_pueden_comprobar_tarjetas_de_la_sesion(self):
        self._con_pasos_viejos()
        self.assertEqual(self._practica_status(1), 403)                                # todavía no se abrió /practica
        self.c.get("/practica")
        self.assertEqual(self.post("/api/practica/comprobar", {"leccion": "hola-mundo", "paso": 0, "respuesta": True}).status_code, 403)
        self.assertEqual(self.post("/api/practica/comprobar", {"leccion": "hola-mundo", "paso": "x"}).status_code, 400)
        self.assertEqual(self.c.post("/api/practica/comprobar", json={}).status_code, 403)   # sin token

    def _practica_status(self, i):
        return self.post("/api/practica/comprobar", {"leccion": "hola-mundo", "paso": i, "respuesta": "mostrar"}).status_code

    # ── proyectos guiados ──
    def test_proyectos_guiados_se_abren_tras_par_o_impar_y_arrancan_desde_el_codigo_anterior(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self.assertEqual(self.c.get("/leccion/proyecto-adivinador").status_code, 302)
        self._terminar_hasta("par-o-impar")
        html = self.c.get("/leccion/proyecto-adivinador").get_data(as_text=True)
        self.assertIn('"inicial"', html)
        self.assertIn("secreto es 7", html)
        self.assertNotIn('"solucion"', html)

    def test_paso_de_proyecto_con_preguntar_se_evalua_con_lo_que_responde_el_chico(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("par-o-impar")
        ruta = "/api/lecciones/proyecto-adivinador/pasos/3/evaluar"
        codigo = ('secreto es 7\nintento es int(preguntar("¿Qué número pensé? "))\n'
                  'si intento == secreto:\n    mostrar "¡Acertaste!"\nsino:\n    mostrar "Casi..."')
        self.assertEqual(self.post(ruta, {"codigo": codigo}).get_json()["pregunta"], "¿Qué número pensé? ")
        for respuesta in ("7", "3"):                                         # acierta o falla: la solución oficial lo acompaña
            r = self.post(ruta, {"codigo": codigo, "entradas": [respuesta]}).get_json()
            self.assertEqual(r["evaluacion"]["estado"], "correcto")
        raro = codigo.replace('"Casi..."', '"Nop"')
        r = self.post(ruta, {"codigo": raro, "entradas": ["3"]}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "incorrecto")

    def test_la_casa_pide_la_leccion_triangulo_y_las_anteriores(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("par-o-impar")
        for dependencia in ("proyecto-adivinador", "proyecto-calculadora"):
            self._dar_por_completa(dependencia)
        self.assertEqual(self.c.get("/leccion/proyecto-casa").status_code, 302)       # falta terminar «Triángulo»
        html = self.c.get("/").get_data(as_text=True)
        self.assertIn("Primero terminá «Triángulo»", html)                             # el camino avisa qué falta
        self._terminar_hasta("dos-variables")
        for dependencia in ("tortuga-avanzar", "tortuga-girar", "cuadrado-a-mano", "cuadrado-repetir", "triangulo"):
            self._dar_por_completa(dependencia)
        self.assertEqual(self.c.get("/leccion/proyecto-casa").status_code, 200)

    def test_el_dibujo_de_la_casa_se_evalua_como_dibujo(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("par-o-impar")
        self._terminar_hasta("dos-variables")
        for dependencia in ("tortuga-avanzar", "tortuga-girar", "cuadrado-a-mano", "cuadrado-repetir", "triangulo",
                            "proyecto-adivinador", "proyecto-calculadora"):
            self._dar_por_completa(dependencia)
        casa = ("repetir 4 veces:\n    avanzar 100\n    girar_der 90\n"
                "avanzar 100\ngirar_der 30\nrepetir 3 veces:\n    avanzar 100\n    girar_der 120")
        r = self.post("/api/lecciones/proyecto-casa/pasos/3/evaluar", {"codigo": casa}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        solo_paredes = "repetir 4 veces:\n    avanzar 100\n    girar_der 90"
        self.assertEqual(self.post("/api/lecciones/proyecto-casa/pasos/3/evaluar", {"codigo": solo_paredes}).get_json()["evaluacion"]["estado"],
                         "incorrecto")

    # ── certificado ──
    def _completar_curso_tortuga(self, perfectas=True):
        self._terminar_hasta("dos-variables")
        for _, lec in contenido.lecciones(contenido.cargar_curso("tortuga")):
            progreso.registrar_paso_leccion(progreso.cargar_progreso(), lec["id"], 0, 0, perfectas, 1)

    def test_el_certificado_solo_existe_al_terminar_el_curso(self):
        self.post("/api/onboarding", {"meta_min": 10, "nombre": "Lua"})
        for ruta in ("/certificado/tortuga", "/certificado/primeros-pasos"):
            r = self.c.get(ruta)
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r.headers["Location"].endswith("/"))
        self.assertEqual(self.c.get("/certificado/inventado").status_code, 404)
        self.assertNotIn("Ver mi certificado", self.c.get("/").get_data(as_text=True))

    def test_certificado_con_nombre_curso_y_numeros(self):
        self.post("/api/onboarding", {"meta_min": 10, "nombre": "Lua"})
        self._completar_curso_tortuga()
        html = self.c.get("/certificado/tortuga").get_data(as_text=True)
        for texto in ("Certificado", "Lua", "Dibujá con la tortuga", ">15<", "lecciones perfectas", "puntos de experiencia"):
            self.assertIn(texto, html)
        self.assertIn("@media print", self.c.get("/static/css/tortu.css").get_data(as_text=True))
        self.assertIn("Ver mi certificado", self.c.get("/").get_data(as_text=True))
        self.assertIn("Mis certificados", self.c.get("/logros").get_data(as_text=True))

    def test_el_certificado_cuenta_solo_las_perfectas_y_escapa_el_nombre(self):
        self.post("/api/onboarding", {"meta_min": 10, "nombre": "<i>Lua</i>"})
        self._completar_curso_tortuga(perfectas=False)
        html = self.c.get("/certificado/tortuga").get_data(as_text=True)
        self.assertIn("<b>0</b>lecciones perfectas", html)
        self.assertNotIn("<i>Lua</i>", html)

    # ── curso de Python real ──
    def test_ejercicio_en_python_se_evalua_y_da_pistas_sin_traducir(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("desafio-final")
        html = self.c.get("/leccion/py-print").get_data(as_text=True)
        self.assertIn('"lenguaje": "python"', html)
        self.assertNotIn("palabras_pista", html)
        ruta = "/api/lecciones/py-print/pasos/6/evaluar"
        r = self.post(ruta, {"codigo": 'nombre = "Lua"\nprint(nombre)'}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertEqual(r["premio"]["xp"], 30)
        r = self.post(ruta, {"codigo": 'print("Lua")'}).get_json()                        # otra forma válida
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        self.assertEqual(self.post(ruta, {"codigo": 'print("Otro")'}).get_json()["evaluacion"]["estado"], "incorrecto")
        pista = self.post("/api/lecciones/py-print/pasos/6/pista").get_json()
        self.assertEqual(pista["texto"], "print, =")                                       # las del autor, no «mostrar»
        for _ in range(2):
            pista = self.post("/api/lecciones/py-print/pasos/6/pista").get_json()
        self.assertEqual(pista["codigo"], 'nombre = "Lua"\nprint(nombre)')
        self.assertNotIn("python", pista)                                                   # ya es Python: no se traduce

    def test_ejercicio_en_python_con_input_pide_la_respuesta_y_luego_evalua(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("desafio-final")
        self._dar_por_completa("py-print")
        ruta = "/api/lecciones/py-input/pasos/6/evaluar"
        codigo = 'nombre = input("¿Cómo te llamás? ")\nprint("Hola " + nombre)'
        r = self.post(ruta, {"codigo": codigo}).get_json()
        self.assertEqual(r["pregunta"], "¿Cómo te llamás? ")
        self.assertNotIn("evaluacion", r)
        r = self.post(ruta, {"codigo": codigo, "entradas": ["Ana"]}).get_json()
        self.assertEqual(r["evaluacion"]["estado"], "correcto")

    def test_explicacion_lado_a_lado_llega_a_la_pagina(self):
        self.post("/api/onboarding", {"meta_min": 10})
        self._terminar_hasta("desafio-final")
        html = self.c.get("/leccion/py-print").get_data(as_text=True)
        self.assertIn('"tortu": "mostrar', html)
        self.assertIn("print(", html)

    def test_al_terminar_el_curso_1_la_siguiente_es_la_primera_del_curso_2(self):
        ultima = leccion.lista_lecciones(contenido.cargar_curso())[-1]["id"]
        self.assertEqual(ultima, "desafio-final")
        self.assertEqual(leccion.siguiente_global(contenido.todos_los_cursos(), ultima)["id"], "tortuga-avanzar")

    def test_la_meta_avanza_con_el_xp(self):
        self.post("/api/onboarding", {"meta_min": 5})                      # 20 XP
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        est = self.c.get("/api/estado", headers=self.h).get_json()
        self.assertEqual((est["xp_hoy"], est["meta_pct"]), (30, 100))
        self.assertIn("Meta cumplida", self.c.get("/").get_data(as_text=True))
        self.assertIn("cumplida", self.c.get("/resumen").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
