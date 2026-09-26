# ADR-003: Estrategia de producto local y validación antes de crecer

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
Los documentos de `docs/experimental/` plantean, a la vez, plataforma, cuentas, backend, pagos, juegos, otras academias y
comunidad: en la práctica, un producto nuevo encima del actual. El producto actual (local, sin cuentas, 4 cursos, 51
lecciones) funciona y todavía no se validó con chicos reales.

## Decisión propuesta
- **TortuScript Desktop** sigue siendo local, offline y gratuito (ver [ADR-013](ADR-013-desktop-y-cloud.md)).
- Los perfiles siguen siendo locales durante esta etapa.
- **No se implementan cuentas ni backend remoto** hasta validar demanda (Puerta 0 del roadmap maestro: los chicos
  terminan el curso y piden más; los padres ven valor).
- El producto avanza por **tramos verticales** que dejan funcionando lo anterior, no por componentes de "la plataforma".
- Cada fase tiene un presupuesto de esfuerzo y una **puerta de decisión**; no hay fecha global de finalización.

## Consecuencias
+ El trabajo inmediato se limita a mejoras locales (Fases 0–2) que no comprometen la arquitectura.
+ La cuenta no aparece como "solución buscando un problema".
− Sin datos remotos, la validación depende de pruebas presenciales con chicos y de exportaciones voluntarias.
