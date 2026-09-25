"""Tests del registro de órdenes de la tortuga (sin dibujar)."""
import unittest

from tortuscript.executor import ejecutar_codigo
from tortuscript.tortuga import ErrorTortuga, Registro, normalizar_color
from tortuscript.translator import TraductorTortuScript
from tortuscript.worker import atender


def correr(tortu):
    r = Registro()
    salida, error, msg = ejecutar_codigo(TraductorTortuScript().traducir_codigo(tortu),
                                         extra_globals=r.globales(), callback_linea=r.callback_linea)
    return r.ordenes, error, msg


class TestRegistro(unittest.TestCase):
    def test_cuadrado_registra_ordenes_con_linea(self):
        ordenes, error, _ = correr("repetir 2 veces:\n    avanzar 100\n    girar_der 90")
        self.assertFalse(error)
        self.assertEqual([(o["o"], o["v"], o["l"]) for o in ordenes],
                         [("avanzar", 100, 2), ("girar_der", 90, 3)] * 2)

    def test_lapiz_y_color_sin_valor(self):
        ordenes, error, _ = correr('color "rojo"\nsubir_lapiz\nbajar_lapiz')
        self.assertFalse(error)
        self.assertEqual(ordenes[0], {"o": "color", "v": "red", "l": 1})
        self.assertNotIn("v", ordenes[1])
        self.assertNotIn("v", ordenes[2])

    def test_colores(self):
        self.assertEqual(normalizar_color("Azul"), "blue")
        self.assertEqual(normalizar_color("marrón"), "saddlebrown")
        self.assertEqual(normalizar_color("tomato"), "tomato")
        self.assertEqual(normalizar_color("#FF8800"), "#ff8800")
        for malo in ("url(x)", "red;x", "", "#12", 5, None):
            with self.subTest(malo=malo), self.assertRaises(ErrorTortuga):
                normalizar_color(malo)

    def test_argumentos_invalidos_se_explican(self):
        for codigo in ('avanzar "cien"', "avanzar 99999", "girar_der Verdadero"):
            with self.subTest(codigo=codigo):
                _, error, msg = correr(codigo)
                self.assertTrue(error)
                self.assertIn("La tortuga no entendió la orden", msg)
                self.assertNotIn("Para curiosos", msg)

    def test_tope_de_ordenes(self):
        ordenes, error, msg = correr("repetir 4000 veces:\n    avanzar 1\n    girar_der 1\n    avanzar 1")
        self.assertTrue(error)
        self.assertEqual(len(ordenes), 5000)
        self.assertIn("demasiadas órdenes", msg)

    def test_las_ordenes_hechas_se_conservan_ante_un_error(self):
        ordenes, error, _ = correr("avanzar 50\nmostrar x")
        self.assertTrue(error)
        self.assertEqual(len(ordenes), 1)

    def test_decimales_permitidos(self):
        ordenes, error, _ = correr("avanzar 2.5")
        self.assertFalse(error)
        self.assertEqual(ordenes[0]["v"], 2.5)


class TestWorkerTortuga(unittest.TestCase):
    def test_op_tortuga_devuelve_ordenes(self):
        r = atender({"op": "tortuga", "fuente": "avanzar 10", "entradas": []})
        self.assertEqual(r["ordenes"], [{"o": "avanzar", "v": 10, "l": 1}])
        self.assertFalse(r["error"])

    def test_ejecutar_comun_no_trae_ordenes(self):
        r = atender({"op": "ejecutar", "fuente": "mostrar 1", "entradas": []})
        self.assertNotIn("ordenes", r)

    def test_pregunta_pendiente_en_tortuga(self):
        r = atender({"op": "tortuga", "fuente": 'n es preguntar("¿Cuánto?")\navanzar int(n)', "entradas": []})
        self.assertEqual(r["pregunta"], "¿Cuánto?")
        r = atender({"op": "tortuga", "fuente": 'n es preguntar("¿Cuánto?")\navanzar int(n)', "entradas": ["30"]})
        self.assertEqual(r["ordenes"][0]["v"], 30)


if __name__ == "__main__":
    unittest.main()
