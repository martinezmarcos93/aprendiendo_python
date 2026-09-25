"""Tests de progreso: guardado atómico, recuperación, perfiles, racha, niveles."""
import json
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import progreso


class BaseTemporal(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._original = progreso.DIRECTORIO
        self._perfil = progreso.PERFIL_ACTUAL
        progreso.DIRECTORIO = self._dir
        progreso.PERFIL_ACTUAL = "default"

    def tearDown(self):
        progreso.DIRECTORIO = self._original
        progreso.PERFIL_ACTUAL = self._perfil
        shutil.rmtree(self._dir)


class TestGuardado(BaseTemporal):
    def test_ida_y_vuelta(self):
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        p2 = progreso.cargar_progreso()
        self.assertEqual(p2["xp_total"], 30)
        self.assertEqual(p2["ejercicios"]["0"]["estrellas"], 3)

    def test_campos_internos_no_se_guardan(self):
        p = progreso.cargar_progreso()
        progreso.guardar_progreso(p)
        data = json.loads(progreso.get_archivo_progreso().read_text(encoding="utf-8"))
        self.assertNotIn("_perfil", data)
        self.assertEqual(data["version"], progreso.VERSION_ESQUEMA)

    def test_json_corrupto_no_se_pierde_y_se_recupera_del_bak(self):
        # Bug P1: antes se arrancaba de cero y el siguiente guardado pisaba el archivo.
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 3, 30)
        progreso.registrar_ejercicio(p, 1, 3, 30)          # crea el .bak con xp=30
        archivo = progreso.get_archivo_progreso()
        archivo.write_text("{ roto", encoding="utf-8")
        recuperado = progreso.cargar_progreso()
        self.assertEqual(recuperado["xp_total"], 30)      # desde el .bak
        apartados = list(self._dir.glob("progreso_default.json.corrupto-*"))
        self.assertEqual(len(apartados), 1)
        self.assertEqual(apartados[0].read_text(encoding="utf-8"), "{ roto")

    def test_json_corrupto_sin_bak_arranca_de_cero_sin_borrar_el_danado(self):
        progreso.get_archivo_progreso().write_text("[]", encoding="utf-8")
        p = progreso.cargar_progreso()
        self.assertEqual(p["xp_total"], 0)
        self.assertTrue(list(self._dir.glob("*.corrupto-*")))

    def test_no_quedan_temporales(self):
        progreso.guardar_progreso(progreso.cargar_progreso())
        self.assertEqual(list(self._dir.glob("*.tmp")), [])

    def test_migra_archivo_viejo(self):
        progreso.get_archivo_progreso().write_text(
            json.dumps({"xp_total": 10, "ejercicios": {}}), encoding="utf-8")
        p = progreso.cargar_progreso()
        self.assertEqual(p["xp_total"], 10)
        self.assertIn("sesion_hoy", p)


class TestPerfiles(BaseTemporal):
    def test_ventana_abierta_no_mezcla_perfiles(self):
        # Bug P3: el progreso cargado con A se guardaba en el archivo de B.
        progreso.set_perfil("ana")
        p_ana = progreso.cargar_progreso()
        progreso.set_perfil("beto")
        progreso.registrar_ejercicio(p_ana, 0, 3, 30)
        self.assertTrue(progreso.get_archivo_progreso("ana").exists())
        self.assertFalse(progreso.get_archivo_progreso("beto").exists())

    def test_sanitizar_perfil(self):
        self.assertEqual(progreso.sanitizar_perfil("../../Etc"), "etc")
        self.assertEqual(progreso.sanitizar_perfil("  Juan Pérez "), "juan_pérez")
        self.assertEqual(progreso.sanitizar_perfil("///"), "")

    def test_perfil_recordado(self):
        self.assertEqual(progreso.perfil_recordado(), "default")
        progreso.recordar_perfil("ana")
        self.assertEqual(progreso.perfil_recordado(), "ana")

    def test_set_perfil_vacio_no_cambia(self):
        progreso.set_perfil("ana")
        self.assertEqual(progreso.set_perfil("***"), "ana")


class TestRachaYSesion(BaseTemporal):
    def test_racha_consecutiva_y_corte(self):
        p = progreso.cargar_progreso()
        d = date(2026, 9, 1)
        progreso.actualizar_racha(p, d)
        progreso.actualizar_racha(p, d + timedelta(days=1))
        self.assertEqual(p["racha"], 2)
        progreso.actualizar_racha(p, d + timedelta(days=5))
        self.assertEqual(p["racha"], 1)
        self.assertEqual(p["racha_max"], 2)

    def test_racha_vigente_se_corta_al_mostrar(self):
        # Bug P5: se mostraba la racha vieja después de días sin jugar.
        p = {"racha": 5, "ultimo_dia": "2026-09-01"}
        self.assertEqual(progreso.racha_vigente(p, date(2026, 9, 2)), 5)
        self.assertEqual(progreso.racha_vigente(p, date(2026, 9, 4)), 0)

    def test_sesion_de_ayer_no_aparece_como_de_hoy(self):
        # Bug P6.
        p = progreso.cargar_progreso()
        p.update({"ultimo_dia": "2026-09-01", "sesion_hoy": [0]})
        p["ejercicios"]["0"] = {"estrellas": 3, "xp": 30, "completado": True}
        ej = [{"titulo": "1", "nivel": 1}]
        self.assertEqual(progreso.resumen_sesion_hoy(p, ej, date(2026, 9, 2))["completados"], [])
        self.assertEqual(len(progreso.resumen_sesion_hoy(p, ej, date(2026, 9, 1))["completados"]), 1)

    def test_xp_solo_sube_si_mejora(self):
        p = progreso.cargar_progreso()
        progreso.registrar_ejercicio(p, 0, 1, 10)
        progreso.registrar_ejercicio(p, 0, 3, 30)
        progreso.registrar_ejercicio(p, 0, 2, 20)
        self.assertEqual(p["xp_total"], 30)


class TestNiveles(unittest.TestCase):
    def test_nivel_maximo_alcanzable(self):
        # Bug P4: con 900 XP posibles no se pasaba del nivel 7.
        from ejercicios import EJERCICIOS
        maximo = len(EJERCICIOS) * 30
        self.assertEqual(progreso.calcular_nivel(maximo)[0], 10)

    def test_barra_no_desborda(self):
        for xp in (0, 49, 50, 799, 800, 900, 5000):
            _, actual, total = progreso.calcular_nivel(xp)
            self.assertLessEqual(actual, total)
            self.assertGreaterEqual(actual, 0)


if __name__ == "__main__":
    unittest.main()
