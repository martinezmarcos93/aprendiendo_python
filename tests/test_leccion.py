"""Motor de lecciones: pasos públicos, comprobación, XP y progreso por lección."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript import contenido, leccion, progreso
from tortuscript.worker import atender

ELEGIR = {"tipo": "elegir", "pregunta": "¿Cuál?", "opciones": ["a", "b", "c"], "correcta": 1}
PREDECIR = {"tipo": "predecir", "codigo": 'mostrar "x"', "opciones": ["x", '"x"'], "correcta": 0, "pista": "Mirá las comillas."}
COMPLETAR = {"tipo": "completar", "consigna": "c", "codigo": '___ "Hola"', "fichas": ["mostrar", "Hola", "sumar"],
             "respuesta": ["mostrar"], "salida": "Hola"}
COMPLETAR2 = {"tipo": "completar", "consigna": "c", "codigo": "a es ___\nb es ___\nmostrar a", "fichas": ["1", "2", "3"],
              "respuesta": ["1", "2"], "salida": "1"}
ORDENAR = {"tipo": "ordenar", "consigna": "o", "lineas": ['mostrar "Hola"', 'mostrar "Chau"', 'mostrar "Fin"']}
ORDEN_LIBRE = {"tipo": "ordenar", "consigna": "o", "lineas": ["a es 1", "b es 2", "mostrar a + b"]}
EXPLICACION = {"tipo": "explicacion", "texto": "t", "codigo": 'mostrar "Hola"'}
ESCRIBIR = {"tipo": "escribir", "consigna": "e", "solucion": 'mostrar "Hola"'}


def ejecutar_real(fuente, entradas):
    r = atender({"op": "ejecutar", "fuente": fuente, "entradas": entradas})
    return None if r["error"] or r["pregunta"] is not None else r["salida_programa"]


class TestPasoPublico(unittest.TestCase):
    def test_nunca_filtra_la_respuesta(self):
        for paso in (ELEGIR, PREDECIR, COMPLETAR, ORDENAR, EXPLICACION, ESCRIBIR):
            publico = leccion.paso_publico(paso, "leccion", 0, 1)
            with self.subTest(tipo=paso["tipo"]):
                for prohibido in ("correcta", "respuesta", "solucion", "salida", "pista"):
                    self.assertNotIn(prohibido, publico)

    def test_mezcla_reproducible_y_completa(self):
        a = leccion.paso_publico(ELEGIR, "x", 3)["opciones"]
        self.assertEqual(a, leccion.paso_publico(ELEGIR, "x", 3)["opciones"])
        self.assertEqual(sorted(a), ["a", "b", "c"])

    def test_ordenar_no_llega_ya_ordenado(self):
        for i in range(30):
            lineas = leccion.paso_publico(ORDENAR, f"l{i}", i)["lineas"]
            self.assertNotEqual(lineas, ORDENAR["lineas"])
            self.assertEqual(sorted(lineas), sorted(ORDENAR["lineas"]))

    def test_completar_cuenta_huecos(self):
        self.assertEqual(leccion.paso_publico(COMPLETAR2, "x", 0)["huecos"], 2)

    def test_escribir_lleva_el_numero_de_ejercicio(self):
        self.assertEqual(leccion.paso_publico(ESCRIBIR, "x", 0, 7)["ejercicio"], 7)


class TestComprobar(unittest.TestCase):
    def test_elegir_y_predecir(self):
        self.assertTrue(leccion.comprobar(ELEGIR, "b")["ok"])
        r = leccion.comprobar(ELEGIR, "a")
        self.assertFalse(r["ok"])
        self.assertIn("pista", r)
        self.assertTrue(r["pista"])                                   # pista genérica
        self.assertEqual(leccion.comprobar(PREDECIR, '"x"')["pista"], "Mirá las comillas.")   # la del autor
        self.assertFalse(leccion.comprobar(ELEGIR, None)["ok"])
        self.assertFalse(leccion.comprobar(ELEGIR, 1)["ok"])          # tiene que ser el texto

    def test_completar_marca_los_huecos_mal(self):
        self.assertTrue(leccion.comprobar(COMPLETAR2, ["1", "2"])["ok"])
        r = leccion.comprobar(COMPLETAR2, ["1", "3"])
        self.assertEqual((r["ok"], r["malos"]), (False, [1]))
        self.assertFalse(leccion.comprobar(COMPLETAR2, ["1"])["ok"])          # faltan huecos
        self.assertFalse(leccion.comprobar(COMPLETAR2, "1,2")["ok"])

    def test_completar_acepta_otra_solucion_con_la_misma_salida(self):
        # a=1,b=1 → muestra 1, igual que la respuesta oficial (a=1,b=2)
        self.assertFalse(leccion.comprobar(COMPLETAR2, ["1", "1"])["ok"])          # sin ejecutar: exacto
        self.assertTrue(leccion.comprobar(COMPLETAR2, ["1", "1"], ejecutar_real)["ok"])
        self.assertFalse(leccion.comprobar(COMPLETAR2, ["2", "1"], ejecutar_real)["ok"])   # muestra 2

    def test_ordenar(self):
        ok = leccion.comprobar(ORDENAR, ORDENAR["lineas"])
        self.assertTrue(ok["ok"])
        r = leccion.comprobar(ORDENAR, [ORDENAR["lineas"][1], ORDENAR["lineas"][0], ORDENAR["lineas"][2]])
        self.assertEqual((r["ok"], r["malos"]), (False, [0, 1]))
        self.assertFalse(leccion.comprobar(ORDENAR, ORDENAR["lineas"][:2])["ok"])

    def test_ordenar_acepta_otro_orden_que_muestra_lo_mismo(self):
        alterno = ["b es 2", "a es 1", "mostrar a + b"]
        self.assertFalse(leccion.comprobar(ORDEN_LIBRE, alterno)["ok"])
        self.assertTrue(leccion.comprobar(ORDEN_LIBRE, alterno, ejecutar_real)["ok"])
        # mostrar antes de definir → error → no vale
        self.assertFalse(leccion.comprobar(ORDEN_LIBRE, ["mostrar a + b", "a es 1", "b es 2"], ejecutar_real)["ok"])

    def test_explicacion_siempre_ok_y_escribir_no_se_comprueba_aca(self):
        self.assertTrue(leccion.comprobar(EXPLICACION, None)["ok"])
        with self.assertRaises(ValueError):
            leccion.comprobar(ESCRIBIR, "x")

    def test_respuesta_correcta(self):
        self.assertEqual(leccion.respuesta_correcta(ELEGIR), "b")
        self.assertEqual(leccion.respuesta_correcta(COMPLETAR2), ["1", "2"])
        self.assertEqual(leccion.respuesta_correcta(ORDENAR), ORDENAR["lineas"])
        self.assertEqual(leccion.respuesta_correcta(ESCRIBIR), 'mostrar "Hola"')
        self.assertIsNone(leccion.respuesta_correcta(EXPLICACION))


class TestXP(unittest.TestCase):
    def test_xp_por_intentos(self):
        self.assertEqual(leccion.xp_por_intentos(1, False), 5)
        self.assertEqual(leccion.xp_por_intentos(3, False), 2)
        self.assertEqual(leccion.xp_por_intentos(1, True), 0)

    def test_ver_respuesta_solo_tras_dos_errores(self):
        self.assertFalse(leccion.puede_ver_respuesta(1))
        self.assertTrue(leccion.puede_ver_respuesta(2))


class TestNavegacion(unittest.TestCase):
    def setUp(self):
        self.curso = contenido.cargar_curso()

    def test_buscar_y_siguiente(self):
        seccion, lec, pos = leccion.buscar_leccion(self.curso, "hola-mundo")
        self.assertEqual((seccion["nivel"], pos), (1, 0))
        self.assertEqual(leccion.leccion_siguiente(self.curso, "hola-mundo")["id"], "texto-o-cuenta")
        ultima = leccion.lista_lecciones(self.curso)[-1]["id"]
        self.assertIsNone(leccion.leccion_siguiente(self.curso, ultima))
        self.assertIsNone(leccion.buscar_leccion(self.curso, "no-existe"))

    def test_lista_lecciones_coincide_con_el_contenido(self):
        self.assertEqual(len(leccion.lista_lecciones(self.curso)), len(contenido.lecciones(self.curso)))

    def test_indices_de_ejercicio_por_leccion(self):
        idx = contenido.indices_ejercicio("hola-mundo")
        self.assertEqual(idx, {5: 0})               # el paso 6 (índice 5) es el escribir → ejercicio 0
        self.assertEqual(contenido.indices_ejercicio("texto-o-cuenta"), {5: 1})

    def test_esta_completada_compatibilidad_con_progreso_viejo(self):
        viejo = {"ejercicios": {"0": {"completado": True, "estrellas": 2}}}
        self.assertTrue(leccion.esta_completada(viejo, "hola-mundo", [0]))
        self.assertFalse(leccion.esta_completada(viejo, "texto-o-cuenta", [1]))
        self.assertFalse(leccion.esta_completada({}, "x", []))                    # sin escribir ni registro
        nuevo = {"lecciones": {"x": {"completada": True}}}
        self.assertTrue(leccion.esta_completada(nuevo, "x", []))


class TestProgresoLecciones(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._orig = progreso.DIRECTORIO
        progreso.DIRECTORIO = self._dir

    def tearDown(self):
        progreso.DIRECTORIO = self._orig
        shutil.rmtree(self._dir)

    def test_completa_al_terminar_todos_los_pasos(self):
        p = progreso.cargar_progreso()
        r = progreso.registrar_paso_leccion(p, "l", 0, 5, True, 2)
        self.assertEqual((r["completa"], r["xp_ganado"], p["xp_total"]), (False, 5, 5))
        r = progreso.registrar_paso_leccion(p, "l", 1, 2, False, 2)
        self.assertTrue(r["completa"] and r["recien_completa"])
        self.assertFalse(r["perfecta"])
        self.assertEqual(p["xp_total"], 7)

    def test_repetir_no_da_xp_doble_pero_si_mejora(self):
        p = progreso.cargar_progreso()
        progreso.registrar_paso_leccion(p, "l", 0, 2, False, 1)
        r = progreso.registrar_paso_leccion(p, "l", 0, 2, False, 1)
        self.assertEqual((r["xp_ganado"], r["recien_completa"], p["xp_total"]), (0, False, 2))
        r = progreso.registrar_paso_leccion(p, "l", 0, 5, True, 1)
        self.assertEqual((r["xp_ganado"], r["perfecta"], p["xp_total"]), (3, True, 5))

    def test_se_guarda_y_sobrevive_al_recargar(self):
        p = progreso.cargar_progreso()
        progreso.registrar_paso_leccion(p, "l", 0, 5, True, 1)
        again = progreso.cargar_progreso()
        self.assertTrue(again["lecciones"]["l"]["completada"])
        self.assertEqual(again["version"], progreso.VERSION_ESQUEMA)

    def test_progreso_viejo_sin_lecciones_se_migra(self):
        (self._dir / "progreso_default.json").write_text(
            '{"version": 2, "xp_total": 30, "ejercicios": {"0": {"completado": true, "estrellas": 3, "xp": 30}}}',
            encoding="utf-8")
        p = progreso.cargar_progreso()
        self.assertEqual(p["lecciones"], {})
        self.assertEqual(p["xp_total"], 30)
        self.assertTrue(p["ejercicios"]["0"]["completado"])


if __name__ == "__main__":
    unittest.main()
