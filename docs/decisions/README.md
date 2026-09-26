# Decisiones de arquitectura (ADR)

## Regla de gobernanza

> **Propuesta ≠ decisión aprobada.** Una ADR en estado *Propuesta* puede orientar el diseño, pero **no autoriza
> implementación**. Solo una ADR *Aceptada* puede usarse como fundamento para modificar la arquitectura o el
> comportamiento. Si una implementación contradice una ADR Aceptada, **primero se modifica la ADR y después el código**.
>
> Solo Marcos cambia el estado de una ADR. Los documentos de `docs/experimental/` son ideas, no decisiones: nada de lo
> que dicen se implementa sin una ADR Aceptada que lo cubra.

Las medidas de endurecimiento que no condicionan el modelo de producto (p. ej. security headers/CSP) no necesitan ADR.

## Tablero

| ADR | Tema | Estado |
|-----|------|--------|
| [ADR-001](ADR-001-migracion-a-web.md) | Migración a web (Flask local) | Aceptada |
| [ADR-002](ADR-002-cursos-como-datos-y-progreso-aditivo.md) | Cursos como datos / progreso aditivo | Aceptada |
| [ADR-003](ADR-003-producto-local-y-validacion.md) | Producto local y validación antes de crecer | Propuesta |
| [ADR-004](ADR-004-diagnostico-y-continuidad.md) | Diagnóstico y continuidad del camino | Propuesta |
| [ADR-005](ADR-005-intereses-locales.md) | Intereses y feedback locales | Propuesta |
| [ADR-006](ADR-006-runtime-educativo-y-de-juegos.md) | Runtime educativo / runtime de juegos | Propuesta |
| [ADR-007](ADR-007-seguridad-runtime-de-juegos.md) | Seguridad del runtime de juegos | Propuesta |
| [ADR-008](ADR-008-alcance-tortugame-v1.md) | Alcance de TortuGame v1 (RPG por turnos) | Propuesta |
| [ADR-009](ADR-009-determinismo.md) | Determinismo y azar controlado (`dado()`) | Propuesta |
| [ADR-010](ADR-010-sin-comunidad-v1.md) | Sin comunidad en la V1 | Propuesta |
| [ADR-011](ADR-011-proyectos-privados.md) | Proyectos privados por defecto | Propuesta |
| [ADR-012](ADR-012-cuenta-adulto-perfiles-hijo.md) | Cuenta adulta → perfiles hijo | Propuesta (implementación no autorizada) |
| [ADR-013](ADR-013-desktop-y-cloud.md) | TortuScript Desktop / Cloud | Propuesta |
| [ADR-014](ADR-014-ejecucion-de-codigo-del-alumno.md) | Ejecución del código del alumno | Propuesta |
