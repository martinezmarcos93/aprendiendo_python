"""Modos de repaso: qué ejercicios ya completados se vuelven a practicar y en qué orden."""
import random

MODOS = {
    "todos": ("🔁", "Todo lo completado", "En el orden original"),
    "imperfectos": ("⭐", "Solo los imperfectos", "Los que todavía no tienen 3 estrellas"),
    "aleatorio": ("🎲", "Orden aleatorio", "Mezclados para practicar sin orden"),
    "dificiles": ("📉", "Los más difíciles", "De menos a más estrellas"),
}


def _completados(progreso, total):
    ej = progreso.get("ejercicios", {})
    return [(i, ej[str(i)].get("estrellas", 0)) for i in range(total)
            if ej.get(str(i), {}).get("completado")]


def contar(progreso, total):
    """(completados, imperfectos) para mostrar en el selector."""
    comp = _completados(progreso, total)
    return len(comp), sum(1 for _, e in comp if e < 3)


def cola_repaso(progreso, modo, total, semilla=None):
    """Índices (base 0) a repasar. `semilla` hace reproducible el modo aleatorio.
    Un modo desconocido devuelve [] (la página lo trata como 404 antes de llamar)."""
    comp = _completados(progreso, total)
    if modo == "todos":
        return [i for i, _ in comp]
    if modo == "imperfectos":
        return [i for i, e in comp if e < 3]
    if modo == "aleatorio":
        cola = [i for i, _ in comp]
        random.Random(semilla).shuffle(cola)
        return cola
    if modo == "dificiles":
        return [i for i, _ in sorted(comp, key=lambda x: x[1])]   # sort estable
    return []
