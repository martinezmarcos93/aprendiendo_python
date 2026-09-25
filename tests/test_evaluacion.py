"""Tests de la comparación de salidas de los ejercicios."""
import unittest

from ui.ejercicios_window import VentanaEjercicios

norm = VentanaEjercicios._normalizar_salida


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
