"""Camino de lecciones, onboarding y meta diaria."""
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tortuscript import contenido, leccion, progreso

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
        self.assertEqual(self.c.get("/static/css/tortu.css").status_code, 200)     # sin redirigir
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
        self.assertIn("0/30", html)

    def test_aprender_lleva_a_la_leccion_actual(self):
        self.post("/api/onboarding", {"meta_min": 10})
        r = self.c.get("/aprender")
        self.assertTrue(r.headers["Location"].endswith("/leccion/hola-mundo"))
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        self.assertTrue(self.c.get("/aprender").headers["Location"].endswith("/leccion/texto-o-cuenta"))

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
