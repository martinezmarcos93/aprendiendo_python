"""Exportar e importar el progreso: ida y vuelta sin pérdidas y rechazo de archivos dañados o ajenos."""
import copy
import unittest

from tortuscript import progreso, respaldo
from tortuscript.respaldo import ErrorImportacion


def un_progreso():
    p = copy.deepcopy(progreso.PROGRESO_INICIAL)
    p.update(xp_total=250, racha=3, ultimo_dia="2026-09-25", logros={"primer-paso": "2026-09-20"})
    p["config"].update(nombre="Lua", experiencia="poquito", meta_min=15, onboarding=True)
    p["config"]["ajustes"]["contraste"] = "alto"
    p["lecciones"] = {"hola-mundo": {"pasos": {"0": {"xp": 5, "perfecto": True}}, "completada": True, "perfecta": True}}
    p["proyectos"] = {"a1b2c3d4": {"nombre": "Mi casa", "tipo": "tortuga", "codigo": "avanzar 10",
                                   "creado": "2026-09-20", "actualizado": "2026-09-21"}}
    p["_perfil"] = "lua"
    return p


class TestExportar(unittest.TestCase):
    def test_el_sobre_identifica_el_formato_y_no_lleva_campos_internos(self):
        sobre = respaldo.exportar(un_progreso(), "lua")
        self.assertEqual((sobre["formato"], sobre["version"], sobre["perfil"]), ("tortuscript-progreso", 1, "lua"))
        self.assertNotIn("_perfil", sobre["progreso"])

    def test_ida_y_vuelta_sin_perdidas(self):
        original = un_progreso()
        importado, sugerido = respaldo.validar(respaldo.exportar(original, "lua"))
        del original["_perfil"]
        self.assertEqual(sugerido, "lua")
        self.assertEqual(importado, progreso._migrar(copy.deepcopy(original)))

    def test_un_progreso_viejo_se_completa_con_los_campos_nuevos(self):
        sobre = respaldo.exportar({"version": 2, "xp_total": 40, "ejercicios": {"0": {"completado": True}}}, "viejo")
        importado, _ = respaldo.validar(sobre)
        self.assertEqual(importado["version"], progreso.VERSION_ESQUEMA)
        self.assertEqual(importado["xp_total"], 40)
        self.assertEqual(importado["proyectos"], {})

    def test_nombre_de_archivo(self):
        from datetime import date
        self.assertEqual(respaldo.nombre_de_archivo("lua", date(2026, 9, 26)), "tortuscript-lua-2026-09-26.json")


class TestImportarRechaza(unittest.TestCase):
    def rechaza(self, sobre, texto):
        with self.assertRaises(ErrorImportacion) as ctx:
            respaldo.validar(sobre)
        self.assertIn(texto, str(ctx.exception))

    def sobre_con(self, **cambios):
        sobre = respaldo.exportar(un_progreso(), "lua")
        sobre["progreso"].update(cambios)
        return sobre

    def test_archivos_que_no_son_un_progreso(self):
        for ajeno in (None, [], "texto", {"formato": "otro"}, {"xp_total": 9999}):
            self.rechaza(ajeno, "no es un progreso de TortuScript")
        self.rechaza({"formato": "tortuscript-progreso", "version": 1}, "le falta el progreso")

    def test_versiones_mas_nuevas(self):
        sobre = respaldo.exportar(un_progreso(), "lua")
        self.rechaza({**sobre, "version": 2}, "versión más nueva")
        self.rechaza(self.sobre_con(version=progreso.VERSION_ESQUEMA + 1), "versión más nueva")

    def test_tipos_invalidos(self):
        self.rechaza(self.sobre_con(xp_total="mucho"), "«xp_total»")
        self.rechaza(self.sobre_con(xp_total=True), "«xp_total»")          # un booleano no es un número
        self.rechaza(self.sobre_con(xp_total=-5), "«xp_total»")
        self.rechaza(self.sobre_con(lecciones=[]), "«lecciones»")
        self.rechaza(self.sobre_con(ultimo_dia=7), "«ultimo_dia»")

    def test_configuracion_invalida(self):
        for cambio, texto in (({"meta_min": 99}, "meta diaria"), ({"experiencia": "hacker"}, "experiencia"),
                              ({"onboarding": "si"}, "«onboarding»")):
            sobre = respaldo.exportar(un_progreso(), "lua")
            sobre["progreso"]["config"].update(cambio)
            self.rechaza(sobre, texto)

    def test_proyectos_invalidos(self):
        malos = ({"x": {"nombre": "a", "tipo": "tortuga", "codigo": ""}},                       # id raro
                 {"ab": {"nombre": "a", "tipo": "virus", "codigo": ""}},                        # tipo desconocido
                 {"ab": {"nombre": "a", "tipo": "tortuga", "codigo": "x" * 5001}},              # código enorme
                 {"ab": {"nombre": " ", "tipo": "tortuga", "codigo": ""}},                      # sin nombre
                 {f"{i:x}": {"nombre": "a", "tipo": "tortuga", "codigo": ""} for i in range(31)})
        for proyectos in malos:
            self.rechaza(self.sobre_con(proyectos=proyectos), "proyecto")


class TestImportarLimpia(unittest.TestCase):
    def test_descarta_campos_desconocidos_y_ajustes_invalidos(self):
        sobre = respaldo.exportar(un_progreso(), "lua")
        sobre["progreso"]["campo_raro"] = {"x": 1}
        sobre["progreso"]["config"]["ajustes"] = {"contraste": "alto", "tam": "gigantesco", "inventado": "si"}
        importado, _ = respaldo.validar(sobre)
        self.assertNotIn("campo_raro", importado)
        self.assertEqual(importado["config"]["ajustes"]["contraste"], "alto")
        self.assertEqual(importado["config"]["ajustes"]["tam"], "normal")                   # vuelve el de fábrica
        self.assertNotIn("inventado", importado["config"]["ajustes"])

    def test_recorta_nombres_largos(self):
        sobre = respaldo.exportar(un_progreso(), "lua")
        sobre["progreso"]["config"]["nombre"] = "N" * 100
        sobre["progreso"]["proyectos"]["a1b2c3d4"]["nombre"] = "P" * 100
        importado, _ = respaldo.validar(sobre)
        self.assertEqual(len(importado["config"]["nombre"]), 30)
        self.assertEqual(len(importado["proyectos"]["a1b2c3d4"]["nombre"]), 40)

    def test_el_perfil_sugerido_se_sanitiza(self):
        sobre = respaldo.exportar(un_progreso(), "../../Hackeo Total!!")
        self.assertEqual(respaldo.validar(sobre)[1], "hackeo_total")
        self.assertEqual(respaldo.validar({**sobre, "perfil": "!!!"})[1], "importado")

    def test_los_intereses_viajan_y_se_limpian(self):
        sobre = respaldo.exportar(un_progreso(), "lua")
        sobre["progreso"]["intereses"] = {"que-crear": {"respuestas": ["juegos", "raro"], "fecha": "2026-09-26"},
                                          "inventada": {"respuestas": ["x"]}}
        importado, _ = respaldo.validar(sobre)
        self.assertEqual(importado["intereses"], {"que-crear": {"respuestas": ["juegos"], "fecha": "2026-09-26"}})

    def test_nombre_libre_nunca_pisa(self):
        self.assertEqual(respaldo.nombre_libre("lua", ["default"]), "lua")
        self.assertEqual(respaldo.nombre_libre("lua", ["lua", "lua_2"]), "lua_3")


if __name__ == "__main__":
    unittest.main()
