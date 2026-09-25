"""Gamificación amable: congelador de racha, reto de 7 días, meta, logros y liga local."""
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tortuscript import contenido, leccion, liga, logros, progreso


class Base(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._orig = (progreso.DIRECTORIO, progreso.PERFIL_ACTUAL)
        progreso.DIRECTORIO = self._dir
        progreso.PERFIL_ACTUAL = "default"

    def tearDown(self):
        progreso.DIRECTORIO, progreso.PERFIL_ACTUAL = self._orig
        shutil.rmtree(self._dir)


def jugar_dias(p, inicio, cantidad):
    """Simula `cantidad` días seguidos jugando a partir de `inicio`."""
    for i in range(cantidad):
        progreso.actualizar_racha(p, inicio + timedelta(days=i))
    return inicio + timedelta(days=cantidad - 1)


class TestCongelador(Base):
    D0 = date(2026, 9, 1)

    def test_se_gana_uno_cada_7_dias_seguidos_y_avisa(self):
        p = progreso.cargar_progreso()
        jugar_dias(p, self.D0, 6)
        self.assertEqual(p["congeladores"], 0)
        progreso.actualizar_racha(p, self.D0 + timedelta(days=6))
        self.assertEqual((p["racha"], p["congeladores"]), (7, 1))
        self.assertEqual([a["tipo"] for a in p["avisos"]], ["congelador_ganado"])
        self.assertEqual(p["stats"]["congeladores_ganados"], 1)

    def test_se_guardan_como_maximo_2(self):
        p = progreso.cargar_progreso()
        jugar_dias(p, self.D0, 21)
        self.assertEqual(p["congeladores"], 2)
        self.assertEqual(p["stats"]["congeladores_ganados"], 3)      # el tercero se ganó aunque no entre
        self.assertEqual(sum(1 for a in p["avisos"] if a["tipo"] == "congelador_ganado"), 2)

    def test_un_dia_de_falta_se_salva_con_congelador(self):
        p = progreso.cargar_progreso()
        ultimo = jugar_dias(p, self.D0, 7)                            # racha 7, 1 congelador
        hoy = ultimo + timedelta(days=2)                              # faltó un día
        self.assertEqual(progreso.racha_vigente(p, hoy), 7)           # sigue viva mientras no juegue
        self.assertTrue(progreso.racha_protegida(p, hoy))
        progreso.actualizar_racha(p, hoy)
        self.assertEqual((p["racha"], p["congeladores"]), (8, 0))
        self.assertEqual(p["dias_congelados"], [str(ultimo + timedelta(days=1))])
        self.assertEqual(p["avisos"][-1]["tipo"], "congelador_usado")

    def test_sin_congelador_o_con_dos_dias_de_falta_se_corta(self):
        p = progreso.cargar_progreso()
        ultimo = jugar_dias(p, self.D0, 3)
        self.assertEqual(progreso.racha_vigente(p, ultimo + timedelta(days=2)), 0)        # sin congelador
        progreso.actualizar_racha(p, ultimo + timedelta(days=2))
        self.assertEqual(p["racha"], 1)
        q = progreso.cargar_progreso("otro")
        ultimo = jugar_dias(q, self.D0, 7)
        self.assertEqual(progreso.racha_vigente(q, ultimo + timedelta(days=3)), 0)        # faltó 2 días
        progreso.actualizar_racha(q, ultimo + timedelta(days=3))
        self.assertEqual((q["racha"], q["congeladores"]), (1, 1))                          # el congelador no se gasta

    def test_reto_de_7_dias(self):
        p = progreso.cargar_progreso()
        self.assertEqual(progreso.reto_de_racha(p, self.D0), (0, 7))
        ultimo = jugar_dias(p, self.D0, 3)
        self.assertEqual(progreso.reto_de_racha(p, ultimo), (3, 7))
        ultimo = jugar_dias(p, self.D0, 7)
        self.assertEqual(progreso.reto_de_racha(p, ultimo), (7, 7))
        ultimo = jugar_dias(p, self.D0, 8)
        self.assertEqual(progreso.reto_de_racha(p, ultimo), (1, 7))

    def test_calendario_marca_los_dias_congelados(self):
        p = progreso.cargar_progreso()
        ultimo = jugar_dias(p, self.D0, 7)
        hoy = ultimo + timedelta(days=2)
        progreso.actualizar_racha(p, hoy)
        cal = progreso.calendario_semana(p, hoy)
        self.assertEqual([d["congelado"] for d in cal].count(True), 1)
        self.assertTrue(cal[-2]["congelado"])
        self.assertFalse(cal[-2]["activo"])


class TestAvisosYMeta(Base):
    def test_tomar_avisos_los_entrega_una_sola_vez_y_persiste(self):
        p = progreso.cargar_progreso()
        progreso.avisar(p, "logro", id="x")
        self.assertEqual(progreso.tomar_avisos(p), [{"tipo": "logro", "id": "x"}])
        self.assertEqual(progreso.tomar_avisos(p), [])
        self.assertEqual(progreso.cargar_progreso()["avisos"], [])

    def test_meta_cumplida_avisa_una_vez_por_dia(self):
        p = progreso.cargar_progreso()                   # meta 10 min = 40 XP
        hoy = date(2026, 9, 25)
        progreso.sumar_xp(p, 30, hoy)
        self.assertEqual(p["avisos"], [])
        progreso.sumar_xp(p, 15, hoy)
        self.assertEqual([a["tipo"] for a in p["avisos"]], ["meta_cumplida"])
        progreso.sumar_xp(p, 50, hoy)
        self.assertEqual(len(p["avisos"]), 1)
        self.assertEqual(p["dias_meta"], ["2026-09-25"])
        progreso.sumar_xp(p, 45, date(2026, 9, 26))
        self.assertEqual(len(p["avisos"]), 2)
        self.assertEqual(len(p["dias_meta"]), 2)

    def test_perfil_viejo_se_migra_con_los_campos_nuevos(self):
        (self._dir / "progreso_default.json").write_text(
            '{"version": 4, "xp_total": 40, "ejercicios": {}, "config": {"onboarding": true, "meta_min": 10}}', encoding="utf-8")
        p = progreso.cargar_progreso()
        self.assertEqual((p["congeladores"], p["logros"], p["avisos"], p["liga"]["nivel"]), (0, {}, [], 0))
        self.assertEqual(p["version"], progreso.VERSION_ESQUEMA)


def camino_de(progreso_):
    indices = {}
    for i, e in enumerate(contenido.ejercicios()):
        indices.setdefault(e["leccion_id"], []).append(i)
    return leccion.estado_cursos(contenido.todos_los_cursos(), progreso_, indices)


class TestLogros(Base):
    def resumen(self, p):
        return logros.resumen_de(p, camino_de(p))

    def test_ids_unicos_y_bien_formados(self):
        self.assertEqual(len(set(logros.IDS)), len(logros.IDS))
        for id_, icono, titulo, descripcion, condicion in logros.LOGROS:
            self.assertTrue(icono and titulo and descripcion and callable(condicion), id_)

    def test_progreso_vacio_no_da_ningun_logro(self):
        p = progreso.cargar_progreso()
        self.assertEqual(logros.cumplidos(p, self.resumen(p)), [])

    def test_primer_paso_y_primera_leccion(self):
        p = progreso.cargar_progreso()
        progreso.registrar_paso_leccion(p, "hola-mundo", 0, 0, True, 6)
        self.assertEqual(logros.revisar(p, self.resumen(p), date(2026, 9, 25)), ["primer-paso"])
        for i in range(1, 6):
            progreso.registrar_paso_leccion(p, "hola-mundo", i, 5, True, 6)
        nuevos = logros.revisar(p, self.resumen(p), date(2026, 9, 25))
        self.assertEqual(sorted(nuevos), ["perfecta", "primera-leccion"])
        self.assertEqual(p["logros"]["perfecta"], "2026-09-25")

    def test_no_se_repiten_y_avisan_una_vez(self):
        p = progreso.cargar_progreso()
        progreso.registrar_paso_leccion(p, "hola-mundo", 0, 0, True, 1)
        logros.revisar(p, self.resumen(p))
        avisos = len([a for a in p["avisos"] if a["tipo"] == "logro"])
        self.assertEqual(logros.revisar(p, self.resumen(p)), [])
        self.assertEqual(len([a for a in p["avisos"] if a["tipo"] == "logro"]), avisos)

    def test_no_es_perfecta_si_hubo_errores(self):
        p = progreso.cargar_progreso()
        for i in range(5):
            progreso.registrar_paso_leccion(p, "hola-mundo", i, 2, i != 2, 6)
        progreso.registrar_paso_leccion(p, "hola-mundo", 5, 0, True, 6)
        self.assertNotIn("perfecta", logros.cumplidos(p, self.resumen(p)))
        self.assertIn("primera-leccion", logros.cumplidos(p, self.resumen(p)))

    def test_cursos_y_racha_y_niveles(self):
        p = progreso.cargar_progreso()
        for _, lec in contenido.lecciones(contenido.cargar_curso("tortuga")):
            progreso.registrar_paso_leccion(p, lec["id"], 0, 0, True, 1)
        p["racha_max"] = 7
        p["xp_total"] = 800
        p["liga"]["nivel"] = 2
        hechos = logros.cumplidos(p, self.resumen(p))
        for esperado in ("artista", "primer-dibujo", "racha-3", "racha-7", "nivel-5", "liga-plata", "liga-oro"):
            self.assertIn(esperado, hechos)
        self.assertNotIn("curso-1", hechos)
        self.assertNotIn("racha-30", hechos)

    def test_catalogo(self):
        p = progreso.cargar_progreso()
        p["logros"] = {"primer-paso": "2026-09-25"}
        cat = logros.catalogo(p)
        self.assertEqual(len(cat), len(logros.LOGROS))
        self.assertTrue(next(c for c in cat if c["id"] == "primer-paso")["ganado"])
        self.assertFalse(next(c for c in cat if c["id"] == "nivel-10")["ganado"])


class TestLiga(unittest.TestCase):
    LUNES = date(2026, 9, 21)                       # lunes de la semana 39
    MIERCOLES = date(2026, 9, 23)
    DOMINGO = date(2026, 9, 27)

    def test_semanas(self):
        self.assertEqual(liga.clave_semana(self.LUNES), "2026-W39")
        self.assertEqual(liga.clave_semana(self.DOMINGO), "2026-W39")
        self.assertEqual(liga.clave_semana(self.DOMINGO + timedelta(days=1)), "2026-W40")
        self.assertEqual(liga.lunes_de(self.DOMINGO), self.LUNES)
        self.assertEqual(liga.dias_restantes(self.LUNES), 6)
        self.assertEqual(liga.dias_restantes(self.DOMINGO), 0)

    def test_xp_de_la_semana_solo_cuenta_esa_semana(self):
        por_dia = {"2026-09-20": 99, "2026-09-21": 10, "2026-09-23": 5, "2026-09-25": 7, "2026-09-28": 50}
        self.assertEqual(liga.xp_de_la_semana(por_dia, self.MIERCOLES), 15)
        self.assertEqual(liga.xp_de_la_semana(por_dia, self.DOMINGO), 22)

    def test_rivales_son_siempre_los_mismos_y_distintos_entre_semanas(self):
        a = liga.rivales("2026-W39", 0, 4)
        self.assertEqual(a, liga.rivales("2026-W39", 0, 4))
        self.assertNotEqual(a, liga.rivales("2026-W40", 0, 4))
        self.assertEqual(len({r["nombre"] for r in a}), 4)
        self.assertEqual(liga.rivales("2026-W39", 0, 0), [])
        base = liga.XP_BASE[0]
        for r in a:
            self.assertTrue(round(base * 0.55) <= r["total"] <= round(base * 1.45) + 1)

    def test_rivales_de_ligas_altas_son_mas_fuertes(self):
        bajos = sum(r["total"] for r in liga.rivales("2026-W39", 0, 4))
        altos = sum(r["total"] for r in liga.rivales("2026-W39", 5, 4))
        self.assertGreater(altos, bajos * 2)

    def test_tabla_completa_el_grupo_con_rivales_y_ordena(self):
        filas = liga.tabla("Lua", 30, {}, 0, self.MIERCOLES)
        self.assertEqual(len(filas), liga.GRUPO)
        self.assertEqual([f["puesto"] for f in filas], [1, 2, 3, 4, 5])
        self.assertEqual(sum(f["yo"] for f in filas), 1)
        self.assertEqual([f["xp"] for f in filas], sorted((f["xp"] for f in filas), reverse=True))

    def test_tabla_con_otros_perfiles_de_la_pc(self):
        filas = liga.tabla("Lua", 10, {"tomi": 500, "ana": 5}, 0, self.MIERCOLES)
        self.assertEqual(len(filas), 5)
        self.assertEqual(filas[0]["nombre"], "tomi")
        self.assertEqual(sum(1 for f in filas if f["icono"] == "🧒"), 2)              # tomi y ana
        muchos = liga.tabla("Lua", 10, {f"p{i}": i for i in range(9)}, 0, self.MIERCOLES)
        self.assertEqual(len(muchos), liga.GRUPO)                                       # el grupo nunca pasa de 5

    def test_los_rivales_avanzan_a_lo_largo_de_la_semana(self):
        rival = liga.rivales("2026-W39", 0, 1)[0]
        xp = [liga.xp_rival_hasta(rival, self.LUNES + timedelta(days=i)) for i in range(7)]
        self.assertEqual(xp, sorted(xp))
        self.assertEqual(xp[-1], rival["total"])

    def test_resumen(self):
        p = {"xp_por_dia": {"2026-09-22": 400}, "liga": {"nivel": 0, "semana": "2026-W39"}, "config": {"nombre": "Lua"}}
        r = liga.resumen(p, {}, self.MIERCOLES)
        self.assertEqual((r["liga"], r["icono"], r["xp"], r["puesto"]), ("Bronce", "🥉", 400, 1))
        self.assertTrue(r["asciende"])
        self.assertEqual(r["dias_restantes"], 4)
        sin_xp = liga.resumen({"liga": {"nivel": 0}, "config": {"nombre": "Lua"}}, {}, self.MIERCOLES)
        self.assertFalse(sin_xp["asciende"])                                             # sin XP no se sube

    def test_cerrar_semana_primera_vez_solo_anota(self):
        p = {"liga": {"nivel": 0, "semana": None}, "xp_por_dia": {"2026-09-22": 999}}
        self.assertIsNone(liga.cerrar_semana(p, lambda d: {}, self.MIERCOLES))
        self.assertEqual(p["liga"], {"nivel": 0, "semana": "2026-W39"})
        self.assertIsNone(liga.cerrar_semana(p, lambda d: {}, self.MIERCOLES))           # misma semana: nada

    def test_ascenso_al_cambiar_de_semana_si_quedo_entre_los_primeros(self):
        p = {"liga": {"nivel": 0, "semana": "2026-W39"}, "xp_por_dia": {"2026-09-22": 900}, "config": {"nombre": "Lua"},
             "avisos": []}
        aviso = liga.cerrar_semana(p, lambda d: {}, self.DOMINGO + timedelta(days=1))
        self.assertEqual((aviso["tipo"], aviso["liga"], aviso["puesto"]), ("liga_asciende", "Plata", 1))
        self.assertEqual(p["liga"], {"nivel": 1, "semana": "2026-W40"})
        self.assertEqual(p["avisos"][-1]["liga"], "Plata")

    def test_no_asciende_sin_xp_o_fuera_de_los_primeros_tres_y_nunca_baja(self):
        siguiente = self.DOMINGO + timedelta(days=1)
        sin_xp = {"liga": {"nivel": 1, "semana": "2026-W39"}, "xp_por_dia": {}, "avisos": []}
        self.assertIsNone(liga.cerrar_semana(sin_xp, lambda d: {}, siguiente))
        self.assertEqual(sin_xp["liga"]["nivel"], 1)
        flojo = {"liga": {"nivel": 0, "semana": "2026-W39"}, "xp_por_dia": {"2026-09-22": 1}, "avisos": []}
        otros = {"a": 1000, "b": 900, "c": 800, "d": 700}                                  # 4 reales más fuertes
        self.assertIsNone(liga.cerrar_semana(flojo, lambda d: otros, siguiente))
        self.assertEqual(flojo["liga"], {"nivel": 0, "semana": "2026-W40"})

    def test_la_liga_mas_alta_no_sube_mas(self):
        p = {"liga": {"nivel": len(liga.LIGAS) - 1, "semana": "2026-W39"}, "xp_por_dia": {"2026-09-22": 9999}, "avisos": []}
        self.assertIsNone(liga.cerrar_semana(p, lambda d: {}, self.DOMINGO + timedelta(days=1)))
        self.assertEqual(p["liga"]["nivel"], len(liga.LIGAS) - 1)

    def test_si_pasan_varias_semanas_se_resuelve_la_ultima_jugada_y_se_actualiza(self):
        p = {"liga": {"nivel": 0, "semana": "2026-W36"}, "xp_por_dia": {}, "avisos": []}
        self.assertIsNone(liga.cerrar_semana(p, lambda d: {}, self.MIERCOLES))
        self.assertEqual(p["liga"]["semana"], "2026-W39")


if __name__ == "__main__":
    unittest.main()
