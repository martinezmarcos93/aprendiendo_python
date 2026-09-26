# ADR-011: Proyectos privados por defecto

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
Se separa de [ADR-010](ADR-010-sin-comunidad-v1.md) porque es una propiedad del modelo de datos y de permisos, no solo
una decisión social.

## Decisión propuesta
Todo proyecto es **privado** del perfil que lo creó. Cualquier estado futuro (`compartido`, `público`, `remixable`)
requiere una ADR posterior y, con cuentas, la autorización del adulto.

## Consecuencias
+ El modelo de datos actual (proyectos locales por perfil) ya cumple la decisión.
− Si algún día se publica, habrá que agregar estado, autoría y control de acceso.
