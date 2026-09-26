# ADR-006: Separación del runtime educativo y el runtime de juegos

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
Hoy TortuScript se traduce a Python y corre en un subproceso local controlado (AST validado, sin `import`, builtins
limitados, límites de tiempo, memoria, pasos y salida). La academia de juegos propone una API propia (TortuGame) que
corre en el navegador. Eso convierte a TortuScript en un lenguaje educativo con **dos destinos**, no en un simple
pseudolenguaje traducido a Python.

## Decisión propuesta
```
Runtime educativo:  TortuScript → Python → subproceso local controlado     (se mantiene)
Runtime de juegos:  TortuScript → TortuGame → intérprete propio → Canvas    (sistema aparte)
```
- Son dos sistemas distintos. **No** se reutiliza el ejecutor educativo para juegos solo porque "ya tiene sandbox".
- `TortuGame → Python/Pygame` queda como **horizonte pedagógico**, no como parte de la arquitectura inicial: no se diseña
  una abstracción que tenga que funcionar igual sobre Python, JS y Pygame.
- El curso piloto "Tortuaria" (RPG por consola) usa el **runtime educativo** y no depende de esta ADR.

## Consecuencias
+ Cada runtime tiene un modelo de seguridad simple y propio.
− El traductor actual solo produce Python: el runtime de juegos necesita su propio parser/intérprete.
