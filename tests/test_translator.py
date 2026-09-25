"""Tests del traductor TortuScript → Python (sin dependencias: unittest)."""
import ast
import unittest

from ejercicios import EJERCICIOS
from translator import TraductorTortuScript, detectar_tipo


class TestTraduccionLinea(unittest.TestCase):
    CASOS = [
        # Básico
        ('x es 5', 'x = 5'),
        ('mostrar "hola", nombre', 'print("hola", nombre)'),
        ('mostrar', 'print()'),
        ('lista es [1, 2, 3]', 'lista = [1, 2, 3]'),
        ('a, b es 1, 2', 'a, b = 1, 2'),
        # Variables con nombre de palabra clave (bug T1/T2)
        ('y es 3', 'y = 3'),
        ('o es 2', 'o = 2'),
        ('mostrar x + y', 'print(x + y)'),
        ('color es "rojo"', 'color = "rojo"'),
        ('mostrar color', 'print(color)'),
        # Operadores lógicos solo en posición de operador
        ('si x > 3 y y < 2:', 'if x > 3 and y < 2:'),
        ('si no terminado:', 'if not terminado:'),
        ('mientras x < 10 y no listo:', 'while x < 10 and not listo:'),
        # `es` en condiciones compara (bug T4)
        ('si edad es 10:', 'if edad == 10:'),
        ('es_par es n % 2 es 0', 'es_par = n % 2 == 0'),
        ('mostrar a es b', 'print(a == b)'),
        # Bloques
        ('sino si x > 3:', 'elif x > 3:'),
        ('sino:', 'else:'),
        ('para i en range(3):', 'for i in range(3):'),
        ('repetir 3 veces:', 'for _ in range(3):'),
        ('repetir n veces:', 'for _ in range(n):'),
        ('si x > 1: mostrar "grande"', 'if x > 1: print("grande")'),
        ('clase Perro hereda de Animal:', 'class Perro(Animal):'),
        ('clase Gato:', 'class Gato:'),
        ('función saludar(n):', 'def saludar(n):'),
        ('Devolver x * 2', 'return x * 2'),
        # Tildes y mayúsculas (bug T6)
        ('Mostrar "hola"', 'print("hola")'),
        ('MOSTRAR "hola"', 'print("hola")'),
        ('mostrá "hola"', 'print("hola")'),          # voseo
        ('Mostrá "hola"', 'print("hola")'),
        ('es_mayor es Verdadero', 'es_mayor = True'),
        # preguntar
        ('resultado es preguntar("Edad? ")', 'resultado = input("Edad? ")'),
        ('nombre es preguntar "¿Nombre?"', 'nombre = input("¿Nombre?")'),
        # Tortuga
        ('avanzar 100', 'avanzar(100)'),
        ('girar_der(90)', 'girar_der(90)'),
        ('bajar_lapiz', 'bajar_lapiz()'),
        ('color "rojo"', 'color("rojo")'),
        # Strings, f-strings y comentarios intactos
        ("mostrar 'no es'", "print('no es')"),
        ('mostrar f"hola {y}"', 'print(f"hola {y}")'),
        ('x es 1  # no cambiar es', 'x = 1  # no cambiar es'),
        ('mostrar (a + b) * 2', 'print((a + b) * 2)'),
        # Python puro pasa sin cambios
        ('x = 5', 'x = 5'),
        ('print("hola es")', 'print("hola es")'),
    ]

    def test_casos(self):
        t = TraductorTortuScript()
        for tortu, python in self.CASOS:
            with self.subTest(tortu=tortu):
                self.assertEqual(t.traducir_linea(tortu), python)


class TestTraduccionCodigo(unittest.TestCase):
    def test_tab_se_convierte_en_espacios(self):
        t = TraductorTortuScript()
        self.assertEqual(t.traducir_codigo('si Verdadero:\n\tmostrar "tab"'),
                         'if True:\n    print("tab")')

    def test_una_linea_por_linea(self):
        t = TraductorTortuScript()
        codigo = 'x es 1\n\n# comentario\nsi x es 1:\n    mostrar "uno"'
        self.assertEqual(len(t.traducir_codigo(codigo).split("\n")), 5)

    def test_linea_incompleta_no_rompe(self):
        t = TraductorTortuScript()
        self.assertEqual(t.traducir_linea('mostrar "sin cerrar'), 'mostrar "sin cerrar')

    def test_soluciones_oficiales_son_python_valido(self):
        t = TraductorTortuScript()
        for ej in EJERCICIOS:
            with self.subTest(ej=ej["titulo"]):
                ast.parse(t.traducir_codigo(ej["solucion"]))

    def test_palabras_usadas_para_pistas(self):
        t = TraductorTortuScript()
        t.traducir_codigo('nombre es preguntar("Nombre: ")\nmostrar "Hola " + nombre')
        self.assertEqual(t.ultimas_palabras, ["es", "preguntar", "mostrar"])


class TestDetectarTipo(unittest.TestCase):
    def test_tipos(self):
        casos = [
            ('x = 5\nprint(x)', 'python'),
            ('mostrar "a"', 'tortuscript'),
            ('print("hola es")', 'python'),       # palabras dentro de strings no cuentan
            ('mostrar "a"\nprint(1)', 'mixto'),
            ('x = 5\nmostrar x', 'tortuscript'),
        ]
        for codigo, esperado in casos:
            with self.subTest(codigo=codigo):
                self.assertEqual(detectar_tipo(codigo), esperado)


if __name__ == "__main__":
    unittest.main()
