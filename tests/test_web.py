"""Tests de la app web (se saltean si Flask no está instalado: la app Tk no lo necesita)."""
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

    # ── páginas ──
    def test_paginas(self):
        for ruta in ("/", "/experimentar", "/ejercicios/1"):
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

    def test_perfiles(self):
        r = self.post("/api/perfil", {"nombre": "../../Lua"}).get_json()
        self.assertEqual(r["actual"], "lua")
        self.assertEqual(self.post("/api/perfil", {"nombre": "///"}).status_code, 400)
        self.assertIn("lua", self.c.get("/api/perfiles", headers=self.h).get_json()["perfiles"])


if __name__ == "__main__":
    unittest.main()
