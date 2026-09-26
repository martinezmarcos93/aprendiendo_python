# ADR-009: Determinismo y azar controlado

## Estado: Aceptada (26/09/2026) — decisión de Marcos; propuesta el mismo día

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
El RPG necesita dados y botín aleatorio, pero el ejecutor no permite `import` (no hay `random`), y la evaluación
automática y el validador de contenido necesitan resultados reproducibles.

## Decisión
- El azar se ofrece como **primitiva controlada** del lenguaje (p. ej. `dado(6)`), no importando `random`.
- Su generador es **determinista con semilla**: mismo código + misma semilla = mismo resultado.
- El validador y la evaluación fijan la semilla; el chico, al jugar, puede recibir una semilla nueva.
- Aplica al piloto "Tortuaria" (runtime educativo) y, como principio, al futuro runtime de juegos.

## Consecuencias
+ Se puede evaluar comportamiento, no solo texto, y los tests de contenido siguen siendo reproducibles.
− Agregar `dado()` toca traductor, ejecutor, validador, Referencia y el traductor a Python real: requiere aceptar esta ADR.
