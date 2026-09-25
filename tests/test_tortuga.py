"""Tests del registro de órdenes de la tortuga (sin dibujar)."""
import unittest

from tortuscript import evaluacion, tortuga
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


def dibujo(tortu):
    return correr(tortu)[0]


CUADRADO = "repetir 4 veces:\n    avanzar 100\n    girar_der 90"


class TestComparacionDeDibujos(unittest.TestCase):
    def test_trazos_de_un_cuadrado(self):
        trs = tortuga.trazos(dibujo(CUADRADO))
        self.assertEqual(len(trs), 4)
        x, y = trs[-1][2], trs[-1][3]
        self.assertAlmostEqual(x, 0, places=6)          # vuelve al origen
        self.assertAlmostEqual(y, 0, places=6)

    def test_mismo_dibujo_de_distinta_forma(self):
        explicito = "avanzar 100\ngirar_der 90\navanzar 100\ngirar_der 90\navanzar 100\ngirar_der 90\navanzar 100"
        partido = "repetir 4 veces:\n    avanzar 50\n    avanzar 50\n    girar_der 90"
        self.assertTrue(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo(explicito)))
        self.assertTrue(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo(partido)))      # 8 avanzar, mismo cuadrado

    def test_espejo_no_es_igual_y_retroceder_da_lo_mismo(self):
        izquierda = "repetir 4 veces:\n    avanzar 100\n    girar_izq 90"          # el cuadrado para el otro lado
        self.assertFalse(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo(izquierda)))
        recta = tortuga.similitud(dibujo("avanzar 100"), dibujo("avanzar 100\nretroceder 100\navanzar 100"))
        self.assertEqual(recta, 1.0)

    def test_distinto_tamano_angulo_o_color(self):
        self.assertFalse(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo("repetir 4 veces:\n    avanzar 90\n    girar_der 90")))
        self.assertFalse(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo("repetir 4 veces:\n    avanzar 100\n    girar_der 89")))
        self.assertFalse(tortuga.mismo_dibujo(dibujo(CUADRADO), dibujo('color "rojo"\n' + CUADRADO)))

    def test_el_lapiz_levantado_no_dibuja(self):
        self.assertEqual(tortuga.trazos(dibujo("subir_lapiz\navanzar 50")), [])
        punteada = "repetir 3 veces:\n    avanzar 10\n    subir_lapiz\n    avanzar 10\n    bajar_lapiz"
        self.assertEqual(len(tortuga.trazos(dibujo(punteada))), 3)

    def test_dibujo_vacio_no_cuenta_como_igual(self):
        self.assertFalse(tortuga.mismo_dibujo([], []))
        self.assertEqual(tortuga.similitud([], []), 1.0)

    def test_evaluar_dibujo(self):
        explicito = "avanzar 100\ngirar_der 90\navanzar 100\ngirar_der 90\navanzar 100\ngirar_der 90\navanzar 100"
        ok = evaluacion.evaluar_dibujo(CUADRADO, dibujo(explicito))
        self.assertEqual(ok["estado"], evaluacion.CORRECTO)
        self.assertEqual(ok["similitud"], 1.0)
        self.assertEqual(len(ok["objetivo"]), 8)
        mal = evaluacion.evaluar_dibujo(CUADRADO, dibujo("avanzar 100"))
        self.assertEqual(mal["estado"], evaluacion.INCORRECTO)
        self.assertEqual(evaluacion.evaluar_dibujo(CUADRADO, [])["estado"], evaluacion.SIN_DIBUJO)

    def test_worker_evaluar_tortuga(self):
        r = atender({"op": "evaluar_tortuga", "fuente": CUADRADO, "solucion": CUADRADO, "entradas": []})
        self.assertEqual(r["evaluacion"]["estado"], "correcto")
        r = atender({"op": "evaluar_tortuga", "fuente": "avanzar 5", "solucion": CUADRADO, "entradas": []})
        self.assertEqual(r["evaluacion"]["estado"], "incorrecto")
        r = atender({"op": "evaluar_tortuga", "fuente": "mostrar x", "solucion": CUADRADO, "entradas": []})
        self.assertTrue(r["error"])
        self.assertNotIn("evaluacion", r)


if __name__ == "__main__":
    unittest.main()
