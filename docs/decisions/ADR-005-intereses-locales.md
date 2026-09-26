# ADR-005: Intereses y feedback locales

## Estado: Aceptada (26/09/2026) — decisión de Marcos; propuesta el mismo día

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
El sistema de intereses ("¿Qué querés crear?", votos) sirve para decidir qué construir. Guardar intereses en el perfil
es inocuo; agregarlos entre muchos chicos implica enviar datos de menores a un servidor.

## Decisión
- Intereses, votos y feedback se guardan **solo en el progreso local** del perfil (campos aditivos).
- **No** hay envío a servidor, telemetría ni analítica online en esta etapa.
- La recolección posible es una **exportación voluntaria** que hace el adulto.
- Guardar lo mínimo: sin nombre real, edad exacta, ubicación, colegio ni redes.
- Las preguntas se hacen **después** de que el chico usó el producto (p. ej. al terminar un curso), no en el onboarding.
- Cualquier agregación remota requiere una ADR nueva, modelo parental y consentimiento.

## Consecuencias
+ Se puede construir ya sin cambiar la arquitectura ni la política de privacidad.
− Los datos de intereses llegan en pequeñas cantidades y a mano.
