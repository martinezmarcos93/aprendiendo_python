"""El contenido de los cursos se valida solo: nunca un ejercicio roto llega a pantalla."""
import unittest

from tortuscript import contenido
from tortuscript.validacion import AVISO, ERROR, validar_curso


def curso_con(*pasos):
    return {"id": "c", "titulo": "C", "secciones": [{"id": "s", "nivel": 1, "titulo": "S", "lecciones": [
        {"id": "l", "titulo": "1. L", "pasos": list(pasos)}]}]}


def errores(*pasos):
    return [h.mensaje for h in validar_curso(curso_con(*pasos)) if h.nivel == ERROR]


EXPL = {"tipo": "explicacion", "texto": "Mirá.", "codigo": 'mostrar "x"'}


class TestCursosReales(unittest.TestCase):
    def test_todos_los_cursos_validan_sin_errores(self):
        cursos = sorted(p.stem for p in contenido.CARPETA.glob("*.json"))
        self.assertTrue(cursos)
        for curso_id in cursos:
            with self.subTest(curso=curso_id):
                malos = [str(h) for h in validar_curso(contenido.cargar_curso(curso_id)) if h.nivel == ERROR]
                self.assertEqual(malos, [])

    def test_ids_de_leccion_unicos_entre_cursos(self):
        vistos = {}
        for p in contenido.CARPETA.glob("*.json"):
            for _, lec in contenido.lecciones(contenido.cargar_curso(p.stem)):
                self.assertNotIn(lec["id"], vistos, f"{lec['id']} está en {p.stem} y en {vistos.get(lec['id'])}")
                vistos[lec["id"]] = p.stem

    def test_el_curso_principal_conserva_sus_30_ejercicios_en_orden(self):
        # El índice de cada 'escribir' es la clave del progreso guardado: no puede cambiar de lugar.
        ej = contenido.ejercicios()
        self.assertEqual(len(ej), 30)
        self.assertEqual([e["nivel"] for e in ej], [1] * 3 + [2] * 3 + [3] * 3 + [4] * 3 + [5] * 3 + [6] * 3 + [7] * 3 + [8] * 9)
        self.assertEqual(ej[0]["solucion"], 'mostrar "Hola mundo"')
        self.assertEqual(ej[3]["solucion"], "edad es 12\nmostrar edad")
        self.assertEqual(ej[29]["leccion_id"], "desafio-final")

    def test_cada_leccion_del_principal_tiene_practica_y_termina_escribiendo(self):
        for _, lec in contenido.lecciones(contenido.cargar_curso()):
            with self.subTest(leccion=lec["id"]):
                tipos = [p["tipo"] for p in lec["pasos"]]
                self.assertGreaterEqual(len(tipos), 4)
                self.assertEqual(tipos[-1], "escribir")
                self.assertEqual(tipos[0], "explicacion")
                self.assertLessEqual(tipos.count("explicacion"), 2)

    def test_el_curso_usa_los_6_tipos_de_paso(self):
        usados = {p["tipo"] for _, _, _, p in contenido.pasos(contenido.cargar_curso())}
        self.assertEqual(usados, set(contenido.TIPOS))


class TestElValidadorAtrapaErrores(unittest.TestCase):
    def test_tipo_desconocido(self):
        self.assertTrue(any("tipo de paso desconocido" in m for m in errores({"tipo": "bailar"})))

    def test_campo_faltante(self):
        self.assertTrue(any("falta el campo" in m for m in errores({"tipo": "elegir", "pregunta": "?"})))

    def test_elegir_correcta_fuera_de_rango_y_opciones_repetidas(self):
        self.assertTrue(any("fuera de rango" in m for m in errores(
            EXPL, {"tipo": "elegir", "pregunta": "?", "opciones": ["a", "b"], "correcta": 5})))
        self.assertTrue(any("repetidas" in m for m in errores(
            EXPL, {"tipo": "elegir", "pregunta": "?", "opciones": ["a", "a"], "correcta": 0})))

    def test_predecir_con_respuesta_equivocada(self):
        m = errores(EXPL, {"tipo": "predecir", "codigo": 'mostrar "x"', "opciones": ["y", "x"], "correcta": 0})
        self.assertTrue(any("la opción correcta dice" in x for x in m))

    def test_predecir_con_dos_respuestas_validas(self):
        m = errores(EXPL, {"tipo": "predecir", "codigo": 'mostrar "x"', "opciones": ["x", "x "], "correcta": 0})
        self.assertTrue(any("repetidas" in x or "también es correcta" in x for x in m))

    def test_completar_cantidad_de_huecos_y_fichas(self):
        self.assertTrue(any("huecos" in m for m in errores(EXPL, {
            "tipo": "completar", "consigna": "c", "codigo": "___ ___", "fichas": ["a"], "respuesta": ["a"]})))
        self.assertTrue(any("no están entre las fichas" in m for m in errores(EXPL, {
            "tipo": "completar", "consigna": "c", "codigo": '___ "x"', "fichas": ["sumar"], "respuesta": ["mostrar"]})))

    def test_completar_que_no_muestra_lo_esperado(self):
        m = errores(EXPL, {"tipo": "completar", "consigna": "c", "codigo": '___ "x"', "fichas": ["mostrar"],
                           "respuesta": ["mostrar"], "salida": "otra cosa"})
        self.assertTrue(any("se esperaba" in x for x in m))

    def test_ordenar_que_no_corre(self):
        self.assertTrue(any("no corre" in m for m in errores(EXPL, {
            "tipo": "ordenar", "consigna": "o", "lineas": ["mostrar a", "a es 1"]})))

    def test_escribir_con_solucion_rota_o_muda(self):
        self.assertTrue(any("no corre" in m for m in errores({"tipo": "escribir", "consigna": "c", "solucion": "mostrar x",
                                                              "forma": "mostrar 1"})))
        self.assertTrue(any("no muestra nada" in m for m in errores({"tipo": "escribir", "consigna": "c",
                                                                     "solucion": "x es 1", "forma": "x es 1"})))

    def test_preguntar_sin_entradas_de_prueba(self):
        m = errores({"tipo": "escribir", "consigna": "c", "solucion": 'a es preguntar("?")\nmostrar a',
                     "forma": 'a es preguntar("?")'})
        self.assertTrue(any("entradas_prueba" in x for x in m))

    def test_usar_una_palabra_antes_de_ensenarla(self):
        m = errores({"tipo": "escribir", "consigna": "c", "solucion": 'mostrar "x"'})
        self.assertTrue(any("antes de enseñarlo" in x for x in m))

    def test_ejemplo_que_no_corre(self):
        self.assertTrue(any("el ejemplo no corre" in m for m in errores(
            {"tipo": "explicacion", "texto": "t", "codigo": "mostrar nada_definido"})))

    def test_ids_repetidos_y_seccion_vacia(self):
        curso = curso_con(EXPL)
        curso["secciones"].append({"id": "s", "nivel": 2, "titulo": "S2", "lecciones": []})
        m = [h.mensaje for h in validar_curso(curso) if h.nivel == ERROR]
        self.assertTrue(any("id de sección repetido" in x for x in m))
        self.assertTrue(any("sección sin lecciones" in x for x in m))
        self.assertTrue(any("no tiene secciones" in h.mensaje for h in validar_curso({"id": "x", "secciones": []})))

    def test_avisos_de_estilo(self):
        largo = {"tipo": "explicacion", "texto": "palabra " * 40, "codigo": 'mostrar "x"'}
        jerga = {"tipo": "explicacion", "texto": "Esto es un string con sintaxis.", "codigo": 'mostrar "x"'}
        tilde = {"tipo": "explicacion", "texto": "Mirá la linea de abajo.", "codigo": 'mostrar "x"'}
        for paso, esperado in ((largo, "texto largo"), (jerga, "jerga"), (tilde, "tilde")):
            avisos = [h.mensaje for h in validar_curso(curso_con(paso)) if h.nivel == AVISO]
            self.assertTrue(any(esperado in a for a in avisos), (esperado, avisos))


if __name__ == "__main__":
    unittest.main()
