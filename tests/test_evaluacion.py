"""Tests de la comparación de salidas de los ejercicios."""
import unittest

from tortuscript.evaluacion import normalizar_salida as norm


class TestNormalizarSalida(unittest.TestCase):
    def test_espacios_alrededor_de_signos_no_importan(self):
        # Devolución de uso: "7+3" se rechazaba contra "7 + 3".
        self.assertEqual(norm("7+3\n10"), norm("7 + 3\n10"))
        self.assertEqual(norm("Mi comida favorita es:pizza"), norm("Mi comida favorita es: pizza"))

    def test_espacios_repetidos_y_finales(self):
        self.assertEqual(norm("Hola   mundo  \n\n"), norm("Hola mundo"))

    def test_palabras_pegadas_si_importan(self):
        self.assertNotEqual(norm("Holamundo"), norm("Hola mundo"))
        self.assertNotEqual(norm("Anatiene11años"), norm("Ana tiene 11 años"))

    def test_mayusculas_y_tildes_importan(self):
        self.assertNotEqual(norm("hola mundo"), norm("Hola mundo"))
        self.assertNotEqual(norm("anos"), norm("años"))

    def test_lineas_distintas_importan(self):
        self.assertNotEqual(norm("7 + 3\n7 + 3"), norm("7 + 3\n10"))


if __name__ == "__main__":
    unittest.main()


class TestEvaluar(unittest.TestCase):
    def _correr(self, codigo, entradas=None):
        from tortuscript.executor import ejecutar_codigo
        from tortuscript.translator import TraductorTortuScript
        detalles = {}
        ejecutar_codigo(TraductorTortuScript().traducir_codigo(codigo),
                        entradas_fijas=entradas, detalles=detalles)
        return detalles

    def test_estados(self):
        from tortuscript import evaluacion as ev
        sol = 'mostrar "Hola mundo"'
        self.assertEqual(ev.evaluar(sol, self._correr('mostrar "Hola mundo"'))["estado"], ev.CORRECTO)
        self.assertEqual(ev.evaluar(sol, self._correr('mostrar "Chau"'))["estado"], ev.INCORRECTO)
        self.assertEqual(ev.evaluar(sol, self._correr('x es 1'))["estado"], ev.SIN_SALIDA)

    def test_preguntar_con_las_mismas_respuestas(self):
        from tortuscript import evaluacion as ev
        sol = 'n es preguntar("¿Nombre? ")\nmostrar "Hola " + n'
        alumno = self._correr('x es preguntar("Decime tu nombre: ")\nmostrar "Hola " + x', ["Lua"])
        self.assertEqual(ev.evaluar(sol, alumno)["estado"], ev.CORRECTO)
        self.assertEqual(ev.evaluar(sol, self._correr('mostrar "Hola Lua"'))["estado"], ev.FALTA_PREGUNTAR)

    def test_estrellas_por_pistas(self):
        from tortuscript.evaluacion import estrellas_por_pistas
        self.assertEqual([estrellas_por_pistas(n) for n in range(5)],
                         [(3, 30), (2, 20), (1, 10), (1, 5), (1, 5)])
