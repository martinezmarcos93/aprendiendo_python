"""Límite de memoria del subproceso: una bomba de memoria termina con un mensaje claro, no congela la compu."""
import subprocess
import sys
import unittest
from pathlib import Path

from tortuscript import limites
from tortuscript.proceso import correr

RAIZ = Path(__file__).resolve().parent.parent


@unittest.skipUnless(sys.platform == "win32", "el Job Object es de Windows")
class TestJobObjectWindows(unittest.TestCase):
    def ejecutar(self, codigo):
        r = subprocess.run([sys.executable, "-c", codigo], cwd=str(RAIZ), capture_output=True, text=True, timeout=60)
        return r.stdout.strip()

    def test_el_tope_corta_una_reserva_enorme(self):
        salida = self.ejecutar(
            "from tortuscript import limites\n"
            "print(limites.limitar_memoria_windows(256 * 1024 * 1024))\n"
            "try:\n    x = 'a' * (1024 ** 3)\n    print('reservo 1 GB')\n"
            "except MemoryError:\n    print('MemoryError')\n")
        self.assertEqual(salida.split("\n"), ["True", "MemoryError"])

    def test_lo_normal_sigue_funcionando_con_el_tope(self):
        salida = self.ejecutar(
            "from tortuscript import limites\n"
            "limites.limitar_memoria_windows(256 * 1024 * 1024)\n"
            "x = 'a' * (50 * 1024 ** 2)\nprint(len(x))\n")
        self.assertEqual(salida, str(50 * 1024 ** 2))


@unittest.skipIf(sys.platform == "win32", "en Windows sí se aplica")
class TestFueraDeWindows(unittest.TestCase):
    def test_no_hace_nada(self):
        self.assertFalse(limites.limitar_memoria_windows())


class TestDeExtremoAExtremo(unittest.TestCase):
    def test_bomba_de_memoria_termina_rapido_con_mensaje_claro(self):
        for fuente in ('x es "a" * 2000000000\nmostrar "listo"', "lista es [0] * 400000000\nmostrar 1"):
            with self.subTest(fuente=fuente.split("\n")[0]):
                r = correr({"op": "ejecutar", "fuente": fuente, "entradas": []})
                self.assertTrue(r["error"])
                self.assertIn("demasiada memoria", r["mensaje"])
                self.assertNotIn("listo", r["salida"])

    def test_un_programa_normal_no_se_ve_afectado(self):
        r = correr({"op": "ejecutar", "fuente": "n es 0\nrepetir 1000 veces:\n    n es n + 1\nmostrar n", "entradas": []})
        self.assertFalse(r["error"])
        self.assertEqual(r["salida"].strip(), "1000")


if __name__ == "__main__":
    unittest.main()
