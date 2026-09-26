# ADR-013: Separación TortuScript Desktop / TortuScript Cloud

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Decisión propuesta
```
                 TORTUSCRIPT
          ┌──────────┴──────────┐
  TORTUSCRIPT DESKTOP    TORTUSCRIPT CLOUD (eventual)
  local · offline        cuentas · sincronización
  gratuito · educativo   servicios · premium
  runtime local
```
- **Desktop no depende de Cloud.** Cloud es una capa de servicios opcional, no la evolución que reemplaza a Desktop.
- Ninguna función de Desktop puede pasar a exigir conexión o cuenta.

## Consecuencias
+ Se preserva la propiedad más fuerte del producto: corre en la compu, sin internet, sin cuentas y sin anuncios.
− Cloud tendrá que convivir con usuarios que nunca se conectan (importación/exportación de perfiles).
