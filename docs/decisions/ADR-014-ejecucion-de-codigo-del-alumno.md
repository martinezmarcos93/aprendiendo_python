# ADR-014: Ejecución del código del alumno

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Decisión propuesta
1. **Ningún servidor remoto o público ejecutará código arbitrario del alumno.**
2. El runtime educativo **local** puede ejecutar el código del alumno en un subproceso controlado, con las restricciones
   actuales ([ADR-001](ADR-001-migracion-a-web.md): AST validado, sin `import`, builtins limitados, límites de tiempo,
   memoria, pasos y salida). Eso no cambia.
3. La eventual ejecución remota de código del alumno es un **cambio arquitectónico mayor** y requiere una ADR
   específica; no queda autorizada implícitamente por esta ni por ninguna otra decisión.

## Consecuencias
+ Elimina el mayor riesgo de seguridad de una versión online (§10 de `SEGURIDAD_SITIO_PROFESIONAL.md`).
− En una versión Cloud, el código sigue corriendo en la compu del chico o en su navegador ([ADR-006](ADR-006-runtime-educativo-y-de-juegos.md), [ADR-007](ADR-007-seguridad-runtime-de-juegos.md)).
