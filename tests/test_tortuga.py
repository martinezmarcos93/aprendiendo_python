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


# Pasillo en L: sube 100, dobla a la derecha 100 y sube 100 hasta la salida (mismo dato que "Laberinto I").
LAB_L = {"paredes": [[-30, 30, -30, -130], [-30, -130, 70, -130], [70, -130, 70, -230], [30, 30, 30, -70],
                     [30, -70, 130, -70], [130, -70, 130, -230], [-30, 30, 30, 30]], "salida": [100, -200]}
CAMINO_L = "avanzar 100\ngirar_der 90\navanzar 100\ngirar_izq 90\navanzar 100"


class TestLaberinto(unittest.TestCase):
    def recorrer(self, tortu, lab=LAB_L):
        ordenes, error, _ = correr(tortu)
        self.assertFalse(error)
        return tortuga.recorrer_laberinto(ordenes, lab)

    def test_el_camino_llega_a_la_salida(self):
        r = self.recorrer(CAMINO_L)
        self.assertEqual((r["estado"], r["linea"]), (tortuga.LLEGO, None))

    def test_cualquier_ruta_que_no_choque_y_termine_en_la_salida_vale(self):
        for otra in ("avanzar 110\ngirar_der 90\navanzar 100\ngirar_izq 90\navanzar 90",       # otros largos
                     "avanzar 50\navanzar 50\ngirar_izq 270\navanzar 100\ngirar_der 270\navanzar 100",  # otros giros
                     CAMINO_L + "\nretroceder 10"):                                            # termina cerca
            self.assertEqual(self.recorrer(otra)["estado"], tortuga.LLEGO, otra)

    def test_chocar_informa_la_linea_y_frena_contra_la_pared(self):
        r = self.recorrer("avanzar 100\ngirar_izq 90\navanzar 100")
        self.assertEqual((r["estado"], r["linea"]), (tortuga.CHOCO, 3))
        self.assertEqual(len(r["ordenes"]), 3)
        self.assertAlmostEqual(r["ordenes"][-1]["v"], 30 - tortuga.MARGEN_PARED, delta=1)   # la pared está a 30

    def test_con_el_lapiz_arriba_tambien_choca(self):
        self.assertEqual(self.recorrer("subir_lapiz\navanzar 300")["estado"], tortuga.CHOCO)

    def test_un_tramo_largo_que_atraviesa_la_pared_choca(self):
        r = self.recorrer("girar_der 90\navanzar 1000")
        self.assertEqual((r["estado"], r["linea"]), (tortuga.CHOCO, 2))

    def test_no_llegar_o_no_moverse(self):
        self.assertEqual(self.recorrer("avanzar 50")["estado"], tortuga.NO_LLEGO)
        self.assertEqual(self.recorrer("girar_der 90")["estado"], tortuga.NO_LLEGO)

    def test_problemas_del_dato(self):
        self.assertIsNone(tortuga.problema_laberinto(LAB_L))
        self.assertIn("paredes", tortuga.problema_laberinto({"paredes": [], "salida": [0, 0]}))
        self.assertIn("pared mal escrita", tortuga.problema_laberinto({"paredes": [[1, 2, 3]], "salida": [0, 0]}))
        self.assertIn("salida", tortuga.problema_laberinto({"paredes": [[50, 0, 50, 10]], "salida": "arriba"}))
        self.assertIn("pegada", tortuga.problema_laberinto({"paredes": [[-10, 2, 10, 2]], "salida": [0, -50]}))

    def test_evaluar_laberinto_exige_las_palabras_pedidas(self):
        ordenes, _, _ = correr(CAMINO_L)
        ev = evaluacion.evaluar_laberinto(ordenes, LAB_L, {"avanzar"}, ["repetir"])
        self.assertEqual((ev["estado"], ev["usar"]), (evaluacion.FALTA_USAR, ["repetir"]))
        self.assertEqual(evaluacion.evaluar_laberinto(ordenes, LAB_L, {"repetir"}, ["repetir"])["estado"],
                         evaluacion.CORRECTO)

    def test_el_worker_evalua_el_laberinto_y_corta_las_ordenes_en_el_choque(self):
        pedido = {"op": "evaluar_tortuga", "fuente": "avanzar 500\ngirar_der 90", "solucion": CAMINO_L,
                  "laberinto": LAB_L}
        r = atender(pedido)
        self.assertEqual((r["evaluacion"]["estado"], r["evaluacion"]["linea"]), ("choque", 1))
        self.assertEqual(len(r["ordenes"]), 1)                                  # el giro no llega a pasar
        self.assertNotIn("objetivo", r["evaluacion"])                           # no hay dibujo objetivo
        con_repetir = atender({**pedido, "fuente": CAMINO_L, "usar": ["repetir"]})
        self.assertEqual(con_repetir["evaluacion"]["estado"], "falta_usar")


if __name__ == "__main__":
    unittest.main()
