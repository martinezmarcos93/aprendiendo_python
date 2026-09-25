"""Tests del ejecutor: salida, depurador, anti-bucle, sandbox, tope de salida, entradas."""
import unittest

from tortuscript import executor
from tortuscript.executor import ejecutar_codigo


class TestEjecucion(unittest.TestCase):
    def test_salida_normal(self):
        salida, error, _ = ejecutar_codigo("a = 1\nb = 2\nprint(a + b)")
        self.assertFalse(error)
        self.assertEqual(salida, "3\n")

    def test_depurador_recibe_cada_linea(self):
        # Bug E1: antes el callback nunca recibía eventos de línea.
        lineas = []
        ejecutar_codigo("a = 1\nb = 2\nprint(a + b)", callback_linea=lineas.append)
        self.assertEqual(lineas, [1, 2, 3])

    def test_depurador_entra_en_funciones_y_bucles(self):
        lineas = []
        codigo = "def f():\n    return 1\nfor _ in range(2):\n    f()"
        ejecutar_codigo(codigo, callback_linea=lineas.append)
        self.assertIn(2, lineas)            # dentro de la función
        self.assertEqual(lineas.count(4), 2)

    def test_bucle_infinito(self):
        _, error, msg = ejecutar_codigo("while True:\n    pass")
        self.assertTrue(error)
        self.assertIn("no termina nunca", msg)

    def test_bucle_infinito_con_llamadas(self):
        # Bug E4: el límite ahora es total, no por función.
        _, error, msg = ejecutar_codigo("def f():\n    pass\nwhile True:\n    f()")
        self.assertTrue(error)
        self.assertIn("no termina nunca", msg)

    def test_recursion_infinita(self):
        _, error, msg = ejecutar_codigo("def f():\n    return f()\nf()")
        self.assertTrue(error)
        self.assertIn("se llama a sí misma", msg)

    def test_stdout_se_restaura(self):
        import sys
        original = sys.stdout
        ejecutar_codigo("print(1/0)")
        self.assertIs(sys.stdout, original)


class TestSandbox(unittest.TestCase):
    def test_escape_por_subclases_bloqueado(self):
        # Bug E2: antes esto llegaba a os.system.
        escape = ("c = [k for k in ().__class__.__base__.__subclasses__() "
                  "if k.__name__ == '_wrap_close'][0]\n"
                  "print(c.__init__.__globals__['system'])")
        salida, error, msg = ejecutar_codigo(escape)
        self.assertTrue(error)
        self.assertEqual(salida, "")
        self.assertIn("no se puede usar", msg.lower())

    def test_import_bloqueado(self):
        _, error, msg = ejecutar_codigo("import os")
        self.assertTrue(error)
        self.assertIn("importar", msg)

    def test_builtins_peligrosos_no_existen(self):
        for nombre in ("open", "eval", "exec", "compile", "globals", "getattr"):
            with self.subTest(nombre=nombre):
                _, error, msg = ejecutar_codigo(f"{nombre}")
                self.assertTrue(error)
                self.assertIn("Nombre desconocido", msg)

    def test_guion_bajo_simple_permitido(self):
        salida, error, _ = ejecutar_codigo("for _ in range(2):\n    print('x')")
        self.assertFalse(error)
        self.assertEqual(salida, "x\nx\n")

    def test_tope_de_salida(self):
        # Bug E3: un print gigante ya no congela la interfaz.
        _, error, msg = ejecutar_codigo("print('a' * (executor_max + 1))".replace(
            "executor_max", str(executor.MAX_SALIDA)))
        self.assertTrue(error)
        self.assertIn("demasiado texto", msg)


class TestEntradas(unittest.TestCase):
    def test_entradas_fijas_sin_dialogo(self):
        detalles = {}
        salida, error, _ = ejecutar_codigo(
            "n = input('Nombre: ')\nprint('Hola ' + n)",
            entradas_fijas=["Ana"], detalles=detalles)
        self.assertFalse(error)
        self.assertEqual(salida, "Nombre: Ana\nHola Ana\n")          # con eco
        self.assertEqual(detalles["salida_programa"], "Hola Ana\n")   # solo prints
        self.assertEqual(detalles["entradas"], ["Ana"])

    def test_entradas_de_mas_devuelven_vacio(self):
        salida, error, _ = ejecutar_codigo("print(input() == '')", entradas_fijas=[])
        self.assertFalse(error)
        self.assertIn("True", salida)


class TestMensajesDeError(unittest.TestCase):
    def test_linea_del_error(self):
        _, _, msg = ejecutar_codigo("a = 1\nb = 2\nprint(c)")
        self.assertIn("Mirá la línea 3", msg)
        self.assertIn("«c»", msg)

    def test_sintaxis_con_linea(self):
        _, _, msg = ejecutar_codigo("x = 1\nif x > 0\n    print(x)")
        self.assertIn("línea 2", msg)
        self.assertIn("dos puntos", msg)

    def test_texto_mas_numero(self):
        _, _, msg = ejecutar_codigo("print('Tengo ' + 12)")
        self.assertIn("mezclando texto con números", msg)


if __name__ == "__main__":
    unittest.main()


class TestEntradaDesacoplada(unittest.TestCase):
    """El ejecutor no depende de ninguna interfaz para preguntar()."""

    def test_sin_forma_de_preguntar_se_detiene_y_avisa(self):
        # Modo web: el programa frena en la primera pregunta sin respuesta.
        detalles = {}
        salida, error, _ = ejecutar_codigo(
            "print('antes')\nn = input('¿Nombre? ')\nprint('Hola ' + n)", detalles=detalles)
        self.assertFalse(error)
        self.assertEqual(detalles["pregunta_pendiente"], "¿Nombre? ")
        self.assertIn("antes", salida)
        self.assertNotIn("Hola", salida)

    def test_reejecutar_con_la_respuesta_termina(self):
        detalles = {}
        salida, error, _ = ejecutar_codigo(
            "n = input('¿Nombre? ')\nprint('Hola ' + n)", entradas_fijas=["Ana"], detalles=detalles)
        self.assertFalse(error)
        self.assertIsNone(detalles["pregunta_pendiente"])
        self.assertIn("Hola Ana", salida)

    def test_sin_respuesta_conocida_el_programa_se_detiene_con_la_pregunta(self):
        # La web pregunta y vuelve a ejecutar con las respuestas acumuladas.
        detalles = {}
        salida, error, _ = ejecutar_codigo("print(input('¿Color? '))", detalles=detalles)
        self.assertFalse(error)
        self.assertEqual(detalles["pregunta_pendiente"], "¿Color? ")
        salida, _, _ = ejecutar_codigo("print(input('¿Color? '))", entradas_fijas=["azul"], detalles=detalles)
        self.assertIn("azul", salida)
        self.assertIsNone(detalles["pregunta_pendiente"])

    def test_try_except_del_alumno_no_frena_el_corte_de_bucle(self):
        codigo = "while True:\n    try:\n        pass\n    except Exception:\n        pass"
        _, error, msg = ejecutar_codigo(codigo)
        self.assertTrue(error)
        self.assertIn("no termina nunca", msg)

    def test_try_except_del_alumno_no_se_traga_la_pregunta(self):
        detalles = {}
        ejecutar_codigo("try:\n    input('?')\nexcept Exception:\n    print('tragada')",
                        detalles=detalles)
        self.assertEqual(detalles["pregunta_pendiente"], "?")
