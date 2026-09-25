"""Referencia (datos), modos de repaso y calendario del resumen."""
import unittest
from datetime import date

from tortuscript import progreso
from tortuscript.referencia import cargar_referencia
from tortuscript.repaso import MODOS, contar, cola_repaso
from tortuscript.translator import TraductorTortuScript


class TestReferencia(unittest.TestCase):
    def ejemplos(self):
        for sec in cargar_referencia()["secciones"]:
            for ej in sec["ejemplos"]:
                yield sec["titulo"], ej

    def test_estructura(self):
        ref = cargar_referencia()
        self.assertTrue(ref["intro"] and ref["pie"])
        for sec in ref["secciones"]:
            self.assertTrue(sec["icono"] and sec["titulo"] and sec["color"] and sec["ejemplos"])

    def test_el_python_es_lo_que_traduce_el_traductor(self):
        t = TraductorTortuScript()
        for titulo, ej in self.ejemplos():
            if ej.get("traducible") is False:
                continue
            with self.subTest(seccion=titulo, ejemplo=ej["descripcion"]):
                self.assertEqual(t.traducir_codigo(ej["tortu"]), ej["python"])

    def test_los_ejemplos_traducidos_son_python_valido(self):
        for titulo, ej in self.ejemplos():
            if ej.get("traducible") is False:
                continue
            with self.subTest(seccion=titulo, ejemplo=ej["descripcion"]):
                compile(ej["python"], "<ej>", "exec")


class TestRepaso(unittest.TestCase):
    P = {"ejercicios": {"0": {"completado": True, "estrellas": 3},
                        "1": {"completado": True, "estrellas": 1},
                        "2": {"completado": True, "estrellas": 2},
                        "3": {"completado": False, "estrellas": 0}}}

    def test_modos(self):
        self.assertEqual(cola_repaso(self.P, "todos", 6), [0, 1, 2])
        self.assertEqual(cola_repaso(self.P, "imperfectos", 6), [1, 2])
        self.assertEqual(cola_repaso(self.P, "dificiles", 6), [1, 2, 0])

    def test_aleatorio_reproducible_y_completo(self):
        a = cola_repaso(self.P, "aleatorio", 6, semilla=7)
        self.assertEqual(a, cola_repaso(self.P, "aleatorio", 6, semilla=7))
        self.assertEqual(sorted(a), [0, 1, 2])

    def test_sin_completados_y_modo_desconocido(self):
        self.assertEqual(cola_repaso({"ejercicios": {}}, "todos", 6), [])
        self.assertEqual(cola_repaso(self.P, "raro", 6), [])

    def test_contar(self):
        self.assertEqual(contar(self.P, 6), (3, 2))

    def test_los_modos_tienen_texto(self):
        self.assertEqual(set(MODOS), {"todos", "imperfectos", "aleatorio", "dificiles"})


class TestCalendario(unittest.TestCase):
    def test_siete_dias_hoy_al_final(self):
        p = {"dias_activo": ["2026-09-24", "2026-09-20"]}
        cal = progreso.calendario_semana(p, date(2026, 9, 25))
        self.assertEqual([d["dia"] for d in cal], [19, 20, 21, 22, 23, 24, 25])
        self.assertEqual([d["activo"] for d in cal], [False, True, False, False, False, True, False])
        self.assertTrue(cal[-1]["hoy"])
        self.assertEqual(sum(d["hoy"] for d in cal), 1)

    def test_cruza_de_mes(self):
        cal = progreso.calendario_semana({}, date(2026, 10, 2))
        self.assertEqual([d["dia"] for d in cal], [26, 27, 28, 29, 30, 1, 2])


if __name__ == "__main__":
    unittest.main()
