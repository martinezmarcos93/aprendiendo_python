"""Intereses locales (ADR-005): encuestas como dato, respuestas solo en el progreso, sin insistir."""
import unittest

from tortuscript import intereses
from tortuscript.validacion import _revisar_texto


class TestEncuestas(unittest.TestCase):
    def test_las_encuestas_estan_bien_formadas_y_escritas_para_chicos(self):
        encuestas = intereses.cargar_encuestas()
        self.assertIn("que-crear", encuestas)
        for e in encuestas.values():
            self.assertEqual(intereses.problemas(e), [], e["id"])
            hallazgos = []
            for texto in [e["pregunta"], e.get("ayuda", "")] + [o["texto"] for o in e["opciones"]]:
                _revisar_texto(texto, e["id"], hallazgos)
            self.assertEqual([h.mensaje for h in hallazgos], [])

    def test_problemas_detecta_errores(self):
        self.assertIn("hay opciones sin id o repetidas", intereses.problemas(
            {"id": "x", "pregunta": "?", "cuando": "curso-terminado", "opciones": [{"id": "a", "texto": "A"}] * 2}))
        self.assertTrue(any("cuando" in m for m in intereses.problemas(
            {"id": "x", "pregunta": "?", "cuando": "siempre", "opciones": [{"id": "a", "texto": "A"}, {"id": "b", "texto": "B"}]})))


class TestResponder(unittest.TestCase):
    def test_guardar_respuestas_validas_sin_repetir_y_en_orden(self):
        p = {}
        intereses.responder(p, "que-crear", ["web", "juegos", "web"])
        self.assertEqual(p["intereses"]["que-crear"]["respuestas"], ["juegos", "web"])
        self.assertIsNone(intereses.pendiente(p, "curso-terminado"))                   # ya contestó

    def test_rechaza_opciones_o_encuestas_desconocidas(self):
        for mal in ([], ["inventada"], "juegos", None):
            with self.assertRaises(ValueError):
                intereses.responder({}, "que-crear", mal)
        with self.assertRaises(ValueError):
            intereses.responder({}, "no-existe", ["juegos"])

    def test_ahora_no_se_respeta(self):
        p = {}
        self.assertEqual(intereses.pendiente(p, "curso-terminado")["id"], "que-crear")
        intereses.omitir(p, "que-crear")
        self.assertIsNone(intereses.pendiente(p, "curso-terminado"))
        self.assertTrue(p["intereses"]["que-crear"]["omitida"])

    def test_limpiar_al_importar(self):
        crudo = {"que-crear": {"respuestas": ["juegos", "hackear", 3], "fecha": "2026-09-26T10:00", "extra": "x"},
                 "inventada": {"respuestas": ["a"]}, "rara": "texto"}
        self.assertEqual(intereses.limpiar(crudo), {"que-crear": {"respuestas": ["juegos"], "fecha": "2026-09-26"}})


if __name__ == "__main__":
    unittest.main()
