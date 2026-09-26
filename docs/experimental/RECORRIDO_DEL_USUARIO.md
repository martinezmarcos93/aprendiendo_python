# Recorrido del usuario: de la primera visita a crear sus propios juegos

> **Estado: EXPERIMENTAL — brainstorming, no aprobado.** Describe la secuencia lógica que vería un usuario que llega de cero.
> Continúa [VISION_PLATAFORMA.md](VISION_PLATAFORMA.md) y [ACADEMIA_DE_JUEGOS_E_INTERESES.md](ACADEMIA_DE_JUEGOS_E_INTERESES.md).
> Lo que hoy existe está en el [README](../../README.md). Los aspectos técnicos y de seguridad no forman parte de este recorrido:
> ver [SEGURIDAD_SITIO_PROFESIONAL.md](SEGURIDAD_SITIO_PROFESIONAL.md).

> Cuentas de padres con perfiles de hijos y lo que falta del producto: [PRODUCTO_COMPLETO_Y_CUENTAS.md](PRODUCTO_COMPLETO_Y_CUENTAS.md).

**Principio:** el usuario percibe solo *entrar → crear perfil → elegir intereses → descubrir su camino → aprender → experimentar → crear →
especializarse → construir proyectos → desarrollar sus propios juegos*. Seguridad, cookies, `robots.txt`, Flask y APIs son capas invisibles.

## 1. Las etapas

| # | Etapa | Qué ve y hace | Estado hoy |
|---|---|---|---|
| 1 | **Entrada** | Mensaje corto ("Aprendé a programar creando cosas") y 3 botones: Empezar / Ya tengo un perfil / ¿Qué puedo aprender? Nunca 50 opciones | Propuesto (hoy se abre directo el selector de perfil o el onboarding) |
| 2 | **Onboarding** | 3–4 pantallas: aprendés jugando · no necesitás saber programar · primero TortuScript (español → Python real) · después Python | Existe un onboarding; el texto se puede alinear a este guion |
| 3 | **Perfil** | "¿Quién está aprendiendo?": apodo, avatar, accesibilidad, meta diaria. Sin email ni contraseña (modelo offline) | Existe (sin avatar) |
| 4 | **Intereses** | "¿Qué te gustaría crear?" (videojuegos, RPG, estrategia, puzzles, web, IA, arte, apps, simulaciones, "no sé todavía") y, opcional, juegos favoritos | Propuesto |
| 5 | **Diagnóstico opcional** | "¿Ya programaste?" Nunca / Un poquito / Bastante / Python. Si ya sabe, prueba rápida para hallar el punto de partida | Propuesto |
| 6 | **Camino** | Pantalla central: dónde está y qué sigue. Hoy lista de lecciones que se desbloquean en orden; a futuro, un **árbol/mapa** | Existe (lineal) |
| 7 | **Primera misión** | "Hacé que la computadora diga algo": `mostrar "Hola"` → ▶ Probar → sale `Hola`. Escribo → ejecuto → pasa algo | Existe como lección 1; puede acortarse a esta forma |
| 8 | **Lección** | Explicación → ejemplo ejecutable → elegir → predecir → completar → ordenar → escribir | Existe (6 tipos de paso) |
| 9 | **Error** | Nunca "ERROR 404": "Casi. La computadora necesita saber qué querés mostrar." + 💡 pista. Sin vidas ni castigos; tras dos fallos se puede ver la respuesta (sin XP) | Existe |
| 10 | **Completar** | ✓ Misión completada · +XP · concepto nuevo · próxima misión. Claro: qué aprendí → qué gané → qué sigue | Existe: el cierre muestra qué aprendí (palabras nuevas), qué practiqué, qué gané (XP, aciertos) y qué sigue (26/09/2026) |
| 11 | **Progreso visible** | Camino con ✓ / → / 🔒, XP, nivel, racha, logros, meta diaria | Existe |
| 12 | **Conceptos en secuencia** | mostrar → variables → preguntar → cuentas → si/sino → repetir → mientras → funciones | Existe (curso 1) |
| 13 | **Herramientas paralelas** | Experimentar, Zona Tortuga, Mis proyectos, Referencia, Repaso, Resumen. No compiten con el Camino: Camino = guiado, Experimentar = laboratorio, Proyectos = creación, Referencia = consulta, Repaso = memoria | Existe |
| 14 | **Primer proyecto** | Combinar lo aprendido (Adivinador, Calculadora, Casa). Cambia la sensación de "hago ejercicios" a "estoy programando" | Existe (3 proyectos guiados) |
| 15 | **Salto a Python real** | `mostrar "Hola"` → `print("Hola")`; TortuScript se desvanece sin sentirse como otra aplicación | Existe (curso 4) |
| 16 | **¿Qué querés crear?** | Nueva decisión tras Python básico: juegos, web, IA, simulaciones, herramientas, datos, arte | Propuesto |
| 17 | **Academia de juegos** | Fundamentos → Personajes → Sistemas (combate, IA) → Mundo (mapas, NPC, misiones) → **Proyecto final: tu propio RPG** | Propuesto |
| 18 | **Aprendizaje guiado por el proyecto** | Cada concepto aparece porque el juego lo necesita (ver §2) | Propuesto |
| 19 | **Proyectos propios / portfolio local** | "Mis juegos": guardar, abrir, duplicar, borrar (hasta 30) | Existe la base; falta el tipo `juego` |
| 20 | **Feedback** | "¿Qué te gustaría aprender ahora?" y campo libre. Se comunica como *"tus respuestas nos ayudan a decidir qué aprenderás próximamente"*, sin prometer | Propuesto |
| 21 | **Progreso a largo plazo** | Perfil con nivel y barras por área (Programación, Python, Videojuegos, RPG), proyectos y logros | Parcial (nivel, logros, certificado) |

## 2. El cambio estructural: del concepto al problema creativo

```
Hoy:       concepto → ejercicio
Objetivo:  problema creativo → concepto necesario → solución → resultado visible
```

| El juego necesita… | Aprende |
|---|---|
| guardar la vida del personaje (`vida es 100`) | variables |
| saber si sobrevive | if |
| atacar diez enemigos | bucles |
| una acción `atacar()` reutilizable | funciones |
| muchos enemigos | listas/diccionarios |
| daño aleatorio | `random` |
| un mapa | coordenadas |
| sprites | gráficos |

El cambio se puede introducir sin romper lo existente (ver ADR-002: contenido como datos, progreso aditivo): un curso nuevo puede plantear
cada lección como misión y reutilizar los mismos 6 tipos de paso.

## 3. Diagrama resumido

```
Acceso → TortuScript → ¿Quién sos? → Perfil y ajustes → ¿Qué querés crear? → Diagnóstico opcional
   → Camino → Primera misión → Explicar → Practicar → Escribir → Ejecutar ─┬─ Error → Pista ─┐
                                                                           └─ Éxito → XP/logro ┴→ Siguiente lección
   → Primer proyecto → Más conceptos → Proyectos guiados → Python real → ¿Qué querés crear?
   → Juegos / Web / IA → Desarrollo de juegos (RPG, estrategia…) → Sistemas de juego → Proyecto propio
   → Portfolio local → Nuevos objetivos → seguir aprendiendo
```

## 4. Qué habría que construir (en orden de bajo riesgo)

1. **Sin tocar el motor:** ajustar textos del onboarding y del cierre de lección; escribir un curso piloto "Tortuaria" (RPG por consola) como datos.
2. **Aditivo y local:** pantalla de intereses y diagnóstico opcional (campos nuevos en el progreso, como `intereses`); encuesta al terminar un curso.
3. **Mayor:** avatar, Camino como mapa/árbol, tipo de proyecto `juego`, portfolio.
4. **Requiere decisiones de arquitectura y política:** recolección agregada de intereses/votos (los datos hoy no salen de la PC) y el runtime de juegos
   (ver los riesgos de ejecución de código en el documento de seguridad).

## 5. Preguntas abiertas
- ¿El diagnóstico inicial reordena el Camino o solo desbloquea lecciones ya vistas?
- ¿Las respuestas de intereses cambian recomendaciones desde el primer día o solo se acumulan?
- ¿Cuánto del Camino se vuelve visual (mapa) antes de tener contenido de juegos que lo justifique?
- Validar todo el recorrido con chicos reales antes de construirlo.
