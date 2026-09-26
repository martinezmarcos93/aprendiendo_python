# ADR-008: Alcance inicial de TortuGame

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Decisión propuesta
**TortuGame v1 = RPG por turnos.** Entidades acotadas: personaje, enemigos, estadísticas, combate, inventario, objetos,
escenas, diálogos, mapa, misiones, estado y guardado.

**Fuera de alcance:** Pygame, multijugador, red, física compleja, 3D, editor libre de niveles, otros géneros.

## Consecuencias
+ Un sistema chico que el chico puede entender entero, y que se puede probar con evaluación determinista ([ADR-009](ADR-009-determinismo.md)).
− Otros géneros (estrategia, plataformas) esperan a que el RPG demuestre tracción (Puerta 2).
