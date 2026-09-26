# Roadmap maestro: de TortuScript local a plataforma educativa

> **Estado: EXPERIMENTAL — propuesta de planificación, no aprobada.** Consolida y entrelaza los cinco documentos anteriores:
> [VISION_PLATAFORMA](VISION_PLATAFORMA.md) · [ACADEMIA_DE_JUEGOS_E_INTERESES](ACADEMIA_DE_JUEGOS_E_INTERESES.md) ·
> [SEGURIDAD_SITIO_PROFESIONAL](SEGURIDAD_SITIO_PROFESIONAL.md) · [RECORRIDO_DEL_USUARIO](RECORRIDO_DEL_USUARIO.md) ·
> [PRODUCTO_COMPLETO_Y_CUENTAS](PRODUCTO_COMPLETO_Y_CUENTAS.md).
> **Las cifras de esfuerzo son estimaciones de orden de magnitud** (no hay medición previa de este tipo de trabajo en el proyecto) y deben revisarse al cerrar cada fase.

> **Gobernanza (26/09/2026):** las decisiones que estructuran este roadmap están en [`docs/decisions/`](../decisions/README.md)
> como ADR-003 a ADR-014, todas en estado *Propuesta*. **Ninguna fase de este documento está autorizada** hasta que su ADR
> pase a *Aceptada*. Cada fase tiene un presupuesto de esfuerzo y una puerta de decisión; **no hay fecha global de
> finalización**. Las cifras no incluyen mantenimiento, soporte, hosting, asesoramiento legal, pentest ni arte.

### Qué entra ahora y qué no

| ✅ Ahora (local, Fases 0–2) | ⛔ Todavía no |
|---|---|
| Pantalla de retorno, navegación global | Backend, cuentas, sincronización |
| Onboarding mínimo (nombre → ¿ya programaste? → `mostrar "Hola"`) | Pagos, suscripciones, freemium |
| Intereses locales, diagnóstico simple (ADR-004/005) | Comunidad, amigos, ranking global, moderación |
| Exportar/importar progreso, ayuda, página de error | Portfolio público, CMS, otras academias |
| Security headers / CSP | Pygame, runtime de juegos completo |
| Curso piloto Tortuaria; pruebas con chicos reales | Mapa complejo, economía interna, analítica online |

## 1. Veredicto sobre la magnitud

| Lectura | Valor |
|---|---|
| Lo que existe hoy | un producto **local y completo**: 4 cursos / 51 lecciones, gamificación, perfiles, proyectos, accesibilidad, 335 tests |
| Lo que se plantea | **un producto nuevo encima del actual**: cuentas y backend, sincronización, panel de padres, pagos, runtime de juegos, 3 disciplinas más, comunidad y operación |
| Esfuerzo total estimado (1 persona a tiempo completo, con asistencia de IA) | **≈ 77–126 semanas-persona** (suma de la tabla §4) en secuencia; con 2–3 personas y contenido en paralelo, **≈ 12–18 meses** |
| Proporción | ~35 % contenido pedagógico, ~35 % backend/cuentas/seguridad/legal, ~20 % experiencia y juegos, ~10 % operación |
| Lo más caro y arriesgado | (1) cuentas de menores + normativa, (2) runtime de juegos, (3) el volumen de contenido |
| Lo más barato y valioso | Fases 0–2: mejoran el producto actual **sin backend** y sirven para validar con chicos reales |

**Conclusión honesta:** el trabajo planteado es de escala de **startup pequeña**, no de proyecto personal de fin de semana. Se puede recorrer por tramos,
pero conviene **comprometerse solo con las Fases 0–2** y decidir el resto con evidencia (uso real, interés de padres, tracción).

## 2. Flujos de trabajo (y cómo se entrelazan)

| Sigla | Flujo | Viene de | Depende de |
|---|---|---|---|
| **A** | Contenido pedagógico (Python I–V, curso "Tortuaria" RPG) | Visión, Academia | motor actual; validador |
| **B** | Experiencia (retorno "Continuar", navegación, onboarding, Camino como mapa, avatar, ayuda, errores) | Recorrido, Producto | — (parte se hace ya) |
| **C** | Intereses, diagnóstico y feedback | Academia, Recorrido | B (pantallas), G (si se agregan datos) |
| **D** | Runtime de juegos en navegador + API TortuGame | Academia | A (contenido lo usa), E (seguridad) |
| **E** | Seguridad y privacidad (P0/P1/P2) | Seguridad | todo lo que sale a internet |
| **F** | Cuentas padre→hijos, panel de padres, consentimientos | Cuentas | E, G |
| **G** | Backend y sincronización (opción C híbrida) | Cuentas | E |
| **H** | Pagos y freemium | Visión | F, G |
| **I** | Otras academias (HTML/CSS, JS, SQL) | Visión | A (motor agnóstico), D (patrón de ejecución en el navegador) |
| **J** | Comunidad: publicar/compartir, moderación | Recorrido, Cuentas | F, E, moderación humana |
| **K** | Operación: admin/CMS, CI/CD, monitoreo, actualizaciones, soporte, SEO | Producto, Seguridad | G |
| **L** | Legal y privacidad de menores | Cuentas, Seguridad | transversal, empieza en la Fase 0 |

### Entrelazados clave
- **B + C + F:** el onboarding (B) pregunta intereses (C) y, con cuentas, se reparte entre el adulto (consentimientos, F) y el niño (apodo, avatar, intereses).
- **D + E:** el runtime de juegos **solo** es aceptable si corre en el navegador; si algún día corre en servidor, E pasa de "P2" a "bloqueante".
- **F + G + H:** no hay pagos sin cuentas; no hay cuentas útiles sin sincronización; ninguna sale sin E (P0/P1).
- **A + I + K:** más disciplinas obligan al motor agnóstico y a un CMS; con 250+ lecciones editar JSON a mano deja de ser sostenible.
- **J** depende de todo lo anterior y **es opcional**: el producto puede ser privado por diseño.

## 3. Fases

Estimaciones en **semanas-persona** (rango). "Puerta" = decisión que se toma con evidencia antes de seguir.

### Fase 0 — Decisiones y validación (2–4 sem) · flujos L, C, B
1. Fijar el alcance real: público objetivo (edad), modelo de negocio (padre paga), país/normativa aplicable.
2. Revisión legal preliminar de datos de menores y consentimiento parental (asesoramiento profesional).
3. Prototipo/ensayo con 5–10 chicos usando **la versión actual** (mide qué les gusta, dónde se traban, si piden juegos).
4. Definir métricas de éxito (retención semana 1/4, lecciones por sesión, proyectos creados).
5. **Puerta 0:** ¿los chicos completan el curso y quieren más? ¿Los padres pagarían? Sin esto, no se sigue con F–H.

### Fase 1 — Producto local mejorado (6–10 sem) · flujos B, C, E(parcial)
1. Pantalla de retorno: "Hola, X. Ayer… Hoy te espera… **[Continuar]**".
2. Navegación global fija (Inicio · Camino · Crear · Proyectos + perfil/ajustes).
3. Onboarding ampliado y alineado al guion (experiencia previa, tiempo diario, dispositivo).
4. **Intereses** y **diagnóstico opcional**: `intereses.py`, campo aditivo en el progreso, `contenido/encuestas/*.json` validable.
5. Exportar/importar progreso (prepara la migración a cuentas).
6. Ayuda del producto, "Reportar un problema" (local) y página de error humana con código de referencia.
7. Cierre de lección reforzado (qué aprendí → qué gané → qué sigue).
8. Endurecimiento barato y reutilizable: headers de seguridad y CSP en la app local.
- **Criterios:** tests verdes, validador en 0 errores, migración aditiva del progreso (v9), revisión de contraste y responsive.
- **Puerta 1:** ¿los cambios mejoran la retención con chicos reales?

> **Estado de la Fase 1 (26/09/2026)** — ver `CHANGELOG.md` y `docs/handoffs/2026-09-26.md`:
> 1 ✅ pantalla de retorno · 2 ✅ ya existía una barra fija (Inicio · Aprender · Experimentar · Tortuga · Practicar ·
> Más); no se reorganizó sin un problema concreto · 3 ✅ en su versión mínima (nombre → ¿ya programaste? → meta); no se
> amplía, para no demorar el primer `mostrar "Hola"` · 4 ⛔ depende de ADR-004 y ADR-005 (Propuesta) · 5 ✅ exportar/importar
> · 6 ✅ ayuda y páginas de error; "reportar un problema" se limita a explicar el código de error (guardar reportes
> depende de ADR-005) · 7 ✅ cierre de lección · 8 ✅ cabeceras y CSP.
> Nada de esto necesitó cambiar el esquema del progreso (sigue en v8). Pendiente de los criterios: revisión automática
> de contraste y responsive (`herramientas/revisar_*.py` necesitan Playwright, que no está instalado). La **Puerta 1**
> y la Fase 0 (probar con chicos reales) no se pueden cerrar desde el código.

### Fase 2 — Contenido piloto "Tortuaria" (RPG por consola) (5–8 sem) · flujo A
1. Diseñar 10–12 lecciones (héroe, estadísticas, enemigo, combate, dados, inventario, pociones, mapa, mazmorra, jefe) con **el motor actual** (datos + validador).
2. Curso de misiones: cada concepto aparece porque el juego lo pide (problema → concepto → solución → resultado).
3. Jefe final: *La Mazmorra del Bug*. Encuesta de un paso al terminar (intereses).
4. Prueba con chicos: ¿lo prefieren al curso de ejercicios?
- **Puerta 2:** define si el eje "juegos" justifica construir el runtime (Fase 3).

### Fase 3 — Runtime de juegos en el navegador (10–16 sem) · flujo D
1. Especificar la API **TortuGame** en español (entidades, escenas, colisiones, combate, inventario, diálogos, guardado).
2. Ejecutor JS en el navegador (canvas), sin servidor y sin `import` libre; API acotada, límites de tiempo/CPU (Web Worker).
3. **Evaluación determinista** con semilla (simulaciones reproducibles) en vez de comparar solo texto/dibujo.
4. Nuevo tipo de proyecto `juego`; guardar/abrir/duplicar.
5. Curso "Game Development I" y puente TortuGame → Python (→ Pygame opcional, fuera de alcance del navegador).
6. Revisión de seguridad específica del runtime (tabla P0 del documento de seguridad).
- **Riesgo alto:** exponer Pygame real obligaría a ejecutar en servidor (evitar; ver Puerta 3).

### Fase 4 — Cuentas y backend mínimo, opción C (16–26 sem) · flujos F, G, E, L
1. Diseño: modelo de datos (adulto, perfil hijo, progreso, proyectos), qué se sincroniza y cómo se resuelven los conflictos.
2. Backend mínimo (auth, perfiles, sync); base de datos con migraciones y privilegios mínimos.
3. Registro/login/logout/recuperación, sesiones seguras, verificación de email, 2FA opcional para el adulto.
4. Perfiles hijo dentro de la cuenta; modo niño vs modo adulto (PIN/contraseña).
5. **Panel de padres** (progreso, tiempo, privacidad, exportar/eliminar datos).
6. Consentimientos separados, política de privacidad visible en la UX, retención de datos.
7. Migración: importar perfiles locales a la cuenta (usa el export de la Fase 1).
8. **Seguridad P0 y P1 completas** (HTTPS/HSTS, cookies, CSRF, rate limiting, logs, backups probados, control de acceso/ownership, secretos, CI con escaneos).
9. Pentest externo antes de abrir al público.
- **Puerta 3:** decisión de infraestructura y costo (hosting, email, soporte). El código de los chicos **sigue ejecutándose en el cliente**; si se decide lo contrario, se replantea la fase.

### Fase 5 — Freemium y pagos (6–10 sem) · flujo H
1. Definir qué es gratis y qué premium (Python inicial gratis; avanzado, web, JS, SQL premium). Regla: **el dinero no compra XP**.
2. Suscripciones, pasarela, facturación, cancelación, período de prueba, pagos fallidos; comprobantes.
3. Control de acceso a contenido premium en el servidor.
4. Cumplimiento fiscal/legal local (consulta profesional).

### Fase 6 — Otras academias (12–20 sem en total, se pueden escalonar) · flujo I
1. Generalizar el motor (evaluador y tipos de paso por disciplina; contenido en `contenido/<disciplina>/`).
2. **HTML + CSS** (3 paneles con vista previa; evaluación de DOM/estilos).
3. **JavaScript** (misma vía del navegador que el runtime de juegos).
4. **SQL** ("investigación detectivesca"; SQLite en WebAssembly, evaluación por resultado de consulta).
5. Cada academia cierra con un proyecto.

### Fase 7 — Comunidad y publicación (12–20 sem + moderación continua) · flujo J
1. Solo con controles parentales: proyectos **privados por defecto**, compartido y público opt-in por el adulto.
2. Reportar, bloquear, revisión humana y automática, antispam; roles de moderación.
3. Perfil público/privado, autor, versión, remixes.
- **Opcional.** Si el producto se decide privado por diseño, esta fase se descarta y **desaparece casi toda la moderación**.

### Fase 8 — Operación y escala (8–12 sem + continuo) · flujo K
1. Panel de administración y CMS educativo (con el validador actual como base) y roles.
2. Monitoreo, alertas, analítica respetuosa (opt-in), CI/CD completo, actualizaciones con rollback y migración del progreso.
3. Soporte (contacto, sugerencias, "¿qué te gustaría que agreguemos?" alimentando el roadmap con intereses).
4. SEO del sitio público (`robots.txt`, `sitemap.xml`, `security.txt`, Open Graph, 404, favicon).
5. Plan Escuela/Institución (docente, varios alumnos) si hay demanda.

## 4. Resumen de esfuerzo

| Fase | Semanas-persona | Se puede paralelizar con | Riesgo |
|---|---|---|---|
| 0 Decisiones y validación | 2–4 | — | Bajo |
| 1 Producto local mejorado | 6–10 | 2 | Bajo |
| 2 Contenido "Tortuaria" | 5–8 | 1, 3 | Bajo–medio |
| 3 Runtime de juegos | 10–16 | 2 | **Alto** |
| 4 Cuentas y backend | 16–26 | 3 (equipo distinto) | **Muy alto** (menores, seguridad, legal) |
| 5 Freemium y pagos | 6–10 | 6 | Medio |
| 6 Otras academias | 12–20 | 5, 7 | Medio (volumen de contenido) |
| 7 Comunidad | 12–20 + continuo | 8 | **Alto** (moderación) |
| 8 Operación | 8–12 + continuo | 5–7 | Medio |
| **Total** | **≈ 77–126** | | |

Supuestos: la cifra crece si hay que **escribir todo el contenido** (Python II–V, web, SQL suman fácilmente 150–250 lecciones frente a las 51 actuales),
si se requiere diseño gráfico/arte (avatar, mundos, mapa), si se suma asesoramiento legal y pentest, y por el mantenimiento posterior (soporte, hosting, actualizaciones),
que **no** está incluido en la tabla.

## 5. Ruta crítica y puertas

```
Fase 0 ─► Fase 1 ─► Fase 2 ──► [Puerta 2: ¿juegos?] ─► Fase 3 ─┐
   │                                                            ├─► Fase 4 ─► [Puerta 3] ─► Fase 5 ─► Fase 6 ─► Fase 7 ─► Fase 8
   └─ L (legal) corre en paralelo desde el principio ───────────┘
```

- **Puerta 0** (validar con chicos y padres) y **Puerta 2** (tracción del eje juegos) son las que más reducen el riesgo de construir de más.
- La ruta crítica pasa por **L → F/G → E**: hasta no cerrar legal, cuentas y seguridad no se abre nada al público.

## 6. Recomendación de compromiso

1. **Comprometerse ahora con las Fases 0–2** (≈ 13–22 semanas): mejoran el producto actual, no exigen backend y generan evidencia.
2. **Diseñar en papel, sin construir**, la Fase 4 y el asesoramiento legal mientras se valida.
3. **Postergar** hasta tener datos: pagos, otras academias y comunidad.
4. Cada fase = rama propia, tests, CHANGELOG y aprobación antes de fusionar a `main` (misma disciplina que en la migración a la web).

## 7. Riesgos transversales
- **Alcance:** cada disciplina y cada género multiplican contenido y mantenimiento. Un producto excelente en Python vale más que cinco a medias.
- **Menores y privacidad:** un error aquí no es reversible; se diseña antes de programar.
- **Sostenibilidad de una sola persona:** operación, soporte y moderación son trabajo continuo, no de una sola vez.
- **Derechos:** mecánicas inspiradas en terceros, pero contenido, nombres y arte propios.
- **Dependencia de decisiones abiertas:** qué se sincroniza, si hay contenido público, edades objetivo, rol escuela.
