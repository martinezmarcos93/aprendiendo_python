# ADR-012: Modelo futuro de cuenta adulta con perfiles hijo

## Estado: Propuesta (26/09/2026) — **implementación NO AUTORIZADA**
Dependencias: validación de producto ([ADR-003](ADR-003-producto-local-y-validacion.md)) y requisitos legales sobre datos de menores.

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
`docs/experimental/PRODUCTO_COMPLETO_Y_CUENTAS.md` registró como "decidido" el modelo padre → hijos y la opción C
(híbrida). Esta ADR lo baja a **Propuesta**: documenta la dirección, pero no la autoriza.

## Decisión propuesta
```
Cuenta adulta (email + contraseña)
 ├── Perfil hijo A   (sin email ni contraseña propios)
 ├── Perfil hijo B
 └── Panel adulto
```
- **Dos contextos de autorización** distintos, no `logged_in + perfil_actual`:
  - *contexto adulto*: autoridad sobre la cuenta (ajustes, datos, privacidad, pagos, hijos);
  - *contexto hijo*: aprender, crear y ver su propio progreso.
- Cada operación del servidor declara qué contexto requiere y verifica pertenencia (*ownership*) en cada llamada:
  `POST /progreso` → hijo · `GET /padre/hijos` → adulto · `DELETE /hijo/<id>` → adulto + reautenticación.
- Pasar de contexto hijo a adulto en una sesión abierta pide PIN o contraseña.
- Arquitectura híbrida (opción C): el aprendizaje y la ejecución siguen siendo locales; la cuenta solo sincroniza.
- **Antes de cualquier API de sincronización** hay que clasificar los datos y fijar la política de cada uno:

  | Categoría | Ejemplos | Política a definir |
  |---|---|---|
  | A. Derivables | XP, nivel, logros | se recalculan desde B |
  | B. Estado educativo | lecciones, mejores resultados, repasos | autoridad del servidor / fusionable |
  | C. Contenido del usuario | proyectos, juegos | última escritura gana / versiones |
  | D. Configuración | accesibilidad, meta diaria | última escritura gana |

## Consecuencias
+ Reduce al mínimo los datos personales de menores.
− Requiere asesoramiento legal y las medidas P0/P1 de `SEGURIDAD_SITIO_PROFESIONAL.md` antes de salir.
