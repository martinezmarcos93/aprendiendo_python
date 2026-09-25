"""Tests de las explicaciones de error."""
import unittest

from tortuscript.error_handler import armar_mensaje_error, explicar_error


class TestExplicaciones(unittest.TestCase):
    def test_compatibilidad_explicar_error(self):
        self.assertIn("División por cero", explicar_error("ZeroDivisionError: division by zero"))

    def test_recursion_y_bucle_no_son_genericos(self):
        # Bug U8: antes caían en "no es un error común".
        for tipo in ("RecursionError", "BucleInfinito"):
            with self.subTest(tipo=tipo):
                self.assertNotIn("poco común", explicar_error(f"{tipo}: x"))

    def test_nombre_concreto_en_name_error(self):
        self.assertIn("«edad»", explicar_error("NameError: name 'edad' is not defined"))

    def test_comillas_sin_cerrar(self):
        try:
            compile('print("hola)', "<tu código>", "exec")
        except SyntaxError as e:
            msg = armar_mensaje_error(e)
        self.assertIn("cerrar las comillas", msg)
        self.assertIn("línea 1", msg)

    def test_detalle_tecnico_no_se_pasa_a_minusculas(self):
        msg = armar_mensaje_error(NameError("name 'Edad' is not defined"))
        self.assertIn("name 'Edad' is not defined", msg)


if __name__ == "__main__":
    unittest.main()
