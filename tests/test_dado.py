"""dado(): azar controlado con semilla (ADR-009)."""
import unittest

from tortuscript import evaluacion
from tortuscript.executor import MAX_CARAS, ejecutar_codigo
from tortuscript.translator import TraductorTortuScript, palabras_usadas
from tortuscript.worker import atender, semilla_del_pedido

TIRAR = "tirada es dado(6)\nmostrar tirada\nmostrar dado(20)\nmostrar dado()"


def correr(tortu, semilla):
    return ejecutar_codigo(TraductorTortuScript().traducir_codigo(tortu), semilla=semilla)


class TestDado(unittest.TestCase):
    def test_misma_semilla_mismas_tiradas_y_en_rango(self):
        a, b = correr(TIRAR, 42), correr(TIRAR, 42)
        self.assertFalse(a[1])
        self.assertEqual(a[0], b[0])
        uno, veinte, seis = (int(x) for x in a[0].split())
        self.assertTrue(1 <= uno <= 6 and 1 <= veinte <= 20 and 1 <= seis <= 6)       # sin número: 6 caras

    def test_semillas_distintas_dan_otras_tiradas(self):
        programa = "repetir 10 veces:\n    mostrar dado(1000)"
        self.assertNotEqual(correr(programa, 1)[0], correr(programa, 2)[0])

    def test_caras_invalidas_se_explican(self):
        for mal in ('dado("seis")', "dado(1)", f"dado({MAX_CARAS + 1})", "dado(2.5)", "dado(verdadero)"):
            with self.subTest(mal):
                salida, error, mensaje = correr(f"mostrar {mal}", 1)
                self.assertTrue(error)
                self.assertIn("🎲 El dado no entendió", mensaje)
                self.assertNotIn("Para curiosos", mensaje)

    def test_el_traductor_lo_deja_igual_y_lo_anota(self):
        self.assertEqual(TraductorTortuScript().traducir_codigo("x es dado(6)"), "x = dado(6)")
        self.assertIn("dado", palabras_usadas("x es dado(6)"))
        self.assertNotIn("dado", palabras_usadas("dado es 3\nmostrar dado"))                 # variable llamada dado


class TestSemillaEnElWorker(unittest.TestCase):
    def test_evaluar_usa_siempre_la_semilla_fija(self):
        for op in ("evaluar", "evaluar_tortuga"):
            self.assertEqual(semilla_del_pedido({"op": op, "semilla": 5}), evaluacion.SEMILLA_EVALUACION)

    def test_jugar_usa_la_del_navegador_o_una_nueva(self):
        self.assertEqual(semilla_del_pedido({"op": "ejecutar", "semilla": 123}), 123)
        for rara in (None, -1, 2 ** 31, "7", True, 1.5):
            s = semilla_del_pedido({"op": "ejecutar", "semilla": rara})
            self.assertTrue(isinstance(s, int) and 0 <= s < 2 ** 31)

    def test_la_respuesta_trae_la_semilla_y_repetirla_repite_las_tiradas(self):
        r = atender({"op": "ejecutar", "fuente": TIRAR})
        otra = atender({"op": "ejecutar", "fuente": TIRAR, "semilla": r["semilla"]})
        self.assertEqual(r["salida_programa"], otra["salida_programa"])

    def test_preguntar_y_dado_no_cambian_entre_vueltas(self):
        fuente = 'a es dado(100)\nnombre es preguntar("¿Nombre?")\nmostrar a'
        primera = atender({"op": "ejecutar", "fuente": fuente})
        self.assertIsNotNone(primera["pregunta"])
        segunda = atender({"op": "ejecutar", "fuente": fuente, "entradas": ["Lua"], "semilla": primera["semilla"]})
        esperado = ejecutar_codigo(TraductorTortuScript().traducir_codigo("mostrar dado(100)"), semilla=primera["semilla"])[0]
        self.assertEqual(segunda["salida_programa"], esperado)

    def test_evaluar_un_programa_con_dado_acepta_otra_forma_de_escribirlo(self):
        solucion = "a es dado(6)\nb es dado(6)\nmostrar a + b"
        otra = "mostrar dado(6) + dado(6)"                                        # mismas tiradas, en el mismo orden
        r = atender({"op": "evaluar", "fuente": otra, "solucion": solucion, "semilla": 99})
        self.assertEqual(r["evaluacion"]["estado"], evaluacion.CORRECTO)
        mal = atender({"op": "evaluar", "fuente": "mostrar dado(6)", "solucion": solucion})
        self.assertEqual(mal["evaluacion"]["estado"], evaluacion.INCORRECTO)


if __name__ == "__main__":
    unittest.main()
