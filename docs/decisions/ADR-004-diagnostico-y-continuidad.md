# ADR-004: Diagnóstico y continuidad del camino educativo

## Estado: Aceptada (26/09/2026) — decisión de Marcos; propuesta el mismo día. **Implementada** el 26/09/2026 (esquema v9)

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
El recorrido propone un diagnóstico opcional ("¿Ya programaste?"). [ADR-002](ADR-002-cursos-como-datos-y-progreso-aditivo.md)
establece que el camino nunca se saltea una lección y que el progreso solo crece. Empezar en la lección 5 obliga a
definir qué pasa con la 1 a la 4 sin inventar una segunda definición de "completado".

## Decisión
```
Diagnóstico → determina un punto de entrada recomendado → NO modifica el orden del curso
```
Si el punto de entrada es la lección 5, las lecciones 1–4 quedan marcadas **"salteadas por diagnóstico"** (campo
aditivo nuevo) y:
- **no** cuentan como completadas;
- **no** otorgan XP, logros ni puntos de liga;
- quedan disponibles para hacerlas después (al hacerlas, se completan normalmente).

La primera versión solo elige un punto de entrada (p. ej. nunca → L1, un poquito → L5, Python → prueba de nivel). No
hay caminos personalizados ni reordenamiento algorítmico.

## Consecuencias
+ Se conserva la semántica de progreso aditivo y la integridad de XP, logros y liga.
− El motor necesita distinguir "salteada" de "pendiente" en la regla de "la que toca".

## Notas de implementación (26/09/2026)
- Campo `salteadas` en el progreso (v9, aditivo). Puntos de entrada: "un poquito" → *Variables* (L4), "bastante" →
  *Condicionales* (L13), al comienzo de una sección. Se elige en la bienvenida; "desde el principio" viene elegido.
- **Precisión:** una lección salteada cuenta como superada **solo para el orden del camino y los `requiere`** (si no,
  quien empieza en *Condicionales* tendría cerrado el curso de la tortuga, que pide *Dos variables*). Para todo lo que
  la ADR enumera (completada, XP, logros, liga) no cuenta, y tampoco para el certificado del curso.

