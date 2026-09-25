# TortuScript → "Mimo para chicos": auditoría y roadmap — 24/09/2026

> Pedido de Marcos: tomar a **Mimo** (mimo.org, app `com.getmimo`) como modelo, clonar
> todo lo que es gratis y volcarlo a chicos de 10-14; auditar funciones, estética y
> ejercicios; y proponer un roadmap para aprobar.
>
> ⚠️ El link de Play Store recibido (`mimo.sz`) es **DJI Mimo** (app de cámaras DJI), no
> la de programación. Se investigó la correcta.

---

## 0. Qué se clona y qué no

| Se clona (mecánicas y pedagogía, no tienen dueño) | No se copia (tiene derechos y además es para adultos) |
|---|---|
| Lecciones de 2 minutos, explicación → práctica interactiva | Textos de sus lecciones y ejercicios |
| Tipos de ejercicio (elegir, completar, ordenar, escribir) | Ilustraciones, íconos, marca, nombre |
| Camino lineal, XP, racha, congelador, liga, logros | Interfaz pixel por pixel |
| Playground, proyectos guiados, certificado, glosario | Su contenido de cursos |

Resultado: **mismo funcionamiento que el Mimo gratuito, con contenido y estética propios
para chicos**, 100% local y offline (filosofía del proyecto).

## 1. Qué es Mimo (investigado)

**Verificado en fuentes** (ver §8):
- 35M+ usuarios, 750K+ reseñas de 5★; cursos de HTML, CSS, JS, TS, React, Python, SQL,
  Swift y 4 "career paths".
- **Formato**: lecciones en segmentos de ~**2 minutos**; *"cada lección empieza con una
  explicación básica y pasa a preguntas interactivas"*. Ciclo **Aprender → Practicar → Construir**.
- **Ejercicios**: predominan *tap-to-fill* (tocar fichas para completar código) y opción
  múltiple; también replicar un fragmento (p. ej. crear un botón) con **vista previa inmediata**.
- **Errores**: pistas específicas; *"podés reintentar antes de ver la respuesta o verla
  directamente"*; varios errores → "Try again".
- **Gamificación**: XP, rachas, logros, **leaderboard por ligas** con ascenso ("si quedás
  arriba en tu liga, subís"); **Streak Freeze** que se compra antes en la tienda y se activa
  solo si faltás un día; **Streak Challenge** de 7 días seguidos; reparación de racha.
- **Vidas (hearts)**: limitadas en el plan gratis; "vidas ilimitadas" es beneficio Pro.
- **Playground**: editor en el celular para experimentar y correr código; se pueden
  "remixar" playgrounds de otros. Gratis: 10 proyectos/playgrounds.
- **Home**: camino lineal que muestra *"exactamente dónde estás y qué sigue"*.
- **Onboarding** de 15 pasos (con un slider para medir experiencia) y paywall temprano.
- **Planes**: Basic gratis (intro de todos los cursos, acceso limitado, tutor IA limitado),
  Pro (todo en móvil, sin anuncios, certificados, vidas ilimitadas) y Max (web, proyectos,
  tutor IA ilimitado). ~USD 5-13/mes.
- **Para chicos** (Common Sense Media): recomendado **12+**; vocabulario difícil ("floating
  point", "sequential order"); **sin audio**, difícil para los más chicos; sugieren pistas
  ante errores repetidos. Educational App Store: 11-18 años, 4/5.
- **Críticas**: mucha opción múltiple y poco tipeo libre; poca profundidad; proyectos chicos.

**No verificado** (el centro de ayuda de Mimo bloquea la lectura automática): cantidad
exacta de vidas y ritmo de recarga, nombres y tamaño de las ligas, XP por actividad, meta
diaria. Se diseñan valores propios.

## 2. Auditoría de TortuScript frente a Mimo

| Área | Mimo | TortuScript hoy | Brecha |
|---|---|---|---|
| **Unidad de aprendizaje** | Lección de 2 min con explicación + 6-10 pasos cortos | Un ejercicio = escribir un programa entero | 🔴 Falta andamiaje: el chico pasa de nada a escribir código completo |
| **Tipos de ejercicio** | Elegir, completar con fichas, ordenar, replicar, correr | Solo "escribí todo" | 🔴 1 tipo contra ~5 |
| **Explicaciones** | Antes de cada práctica | No hay (la Referencia está aparte) | 🔴 |
| **Feedback** | Inmediato por paso, con pista | Al final del programa | 🟠 |
| **Camino / home** | Camino lineal visible | Menú de botones + Mapa aparte | 🟠 |
| **Onboarding** | 15 pasos, nivel y meta | Ninguno | 🟡 |
| **XP / nivel / racha** | Sí | Sí ✅ | — |
| **Meta diaria / congelador / reto 7 días** | Sí | No | 🟡 |
| **Ligas** | Semanales online | No | 🟡 (local) |
| **Logros** | Sí | No | 🟡 |
| **Vidas** | Sí (limitadas gratis) | No | Decisión (§5) |
| **Playground** | Sí, guardable, remix | Experimentar + Tortuga, **no se guarda** | 🟠 |
| **Proyectos guiados** | Sí | No | 🟠 |
| **Certificado** | Pro | No | 🟡 (gratis acá) |
| **Glosario** | Referencia | Referencia ✅ | — |
| **Repaso** | Práctica | Repaso con 4 modos ✅ | Falta espaciado |
| **Contenido** | Miles de lecciones | 30 ejercicios | 🔴 |
| **Validación de contenido** | (interna) | **Manual, ejercicio por ejercicio** | 🔴 *el dolor actual* |

**Estética:** Mimo se ve moderno (tarjetas redondeadas, animaciones, celebraciones). Tk puro
limita bordes redondeados, animaciones y tipografías; se ve "de escritorio viejo".

**Lo que TortuScript tiene y Mimo no:** lenguaje en español (TortuScript), traducción a
Python en vivo, tortuga gráfica con depurador paso a paso, 100% offline y sin anuncios.
**Se conserva todo.**

## 3. Principios del rediseño

1. **El contenido es dato, no código**: lecciones en archivos JSON, un motor que los muestra.
2. **Todo el contenido se valida solo** (fin del "probar ejercicio por ejercicio"): un
   script corre cada respuesta, cada fragmento y cada salida esperada y avisa qué está mal.
3. **Andamiaje estilo Mimo**: explicar → reconocer (elegir) → completar → ordenar → escribir.
4. **Gamificación amable**: premiar constancia sin castigar; nada de presión ni compras.
5. **Local-first**: sin cuentas ni internet; las ligas compiten entre perfiles de la misma PC.
6. **Lenguaje para 10 años**: frases cortas, sin jerga, y audio opcional (lo que le falta a Mimo).

## 4. Roadmap (para aprobar)

Estimación en sesiones de trabajo como las de hoy. Cada fase termina con tests en verde,
commit y una prueba tuya de 10 minutos.

### Fase 0 — Contenido como datos + validador automático (1-2 sesiones) ⭐ primero
- Formato JSON de curso → secciones → lecciones → pasos, con esquema documentado.
- Migrar los 30 ejercicios actuales a ese formato (ninguno se pierde).
- `validar_contenido.py`: para **cada paso** verifica que la respuesta correcta sea
  correcta, que las incorrectas no lo sean, que todo código traduzca y corra, que la salida
  esperada coincida, que la "Forma" aparezca solo la primera vez, y marca frases largas o
  palabras difíciles. Corre dentro de los tests.
- **Resultado**: nunca más un ejercicio roto llega a pantalla.

### Fase 1 — Motor de lecciones con 6 tipos de paso (3-4 sesiones)
| Tipo | Qué hace el chico | Inspirado en |
|---|---|---|
| Explicación | Lee una tarjeta con un ejemplo que puede ejecutar | Mimo (explainer) |
| Elegir | Toca la opción correcta (código o resultado) | Mimo (multiple choice) |
| Completar con fichas | Toca fichas para llenar huecos en el código | Mimo (tap-to-fill) |
| Ordenar líneas | Arrastra o toca líneas para armar el programa | Parsons problems |
| Predecir la salida | Dice qué va a mostrar antes de correrlo | Khan / Brilliant |
| Escribir código | Escribe y ejecuta (el tipo actual) | Mimo (replicar) |
- Feedback por paso con pista; "Reintentar" o "Ver respuesta"; barra de progreso de la lección.
- Lógica en un módulo puro con tests; la UI solo dibuja.

### Fase 2 — Home tipo camino + onboarding + meta diaria (2 sesiones)
- Home = camino lineal con la lección actual destacada (reemplaza el menú de botones;
  Experimentar, Tortuga y Referencia pasan a una barra).
- Onboarding corto para chicos: nombre del perfil, "¿ya programaste alguna vez?", meta
  diaria (5 / 10 / 15 minutos).

### Fase 3 — Gamificación completa y amable (2-3 sesiones)
- XP por paso y por lección; meta diaria con anillo de progreso.
- Racha con **congelador que se gana** (no se compra) y reto de 7 días.
- Logros (primera lección, 7 días, primer dibujo, 10 lecciones perfectas, etc.).
- Liga semanal **local** entre perfiles de la PC, o contra "rivales" simulados si hay un solo perfil.
- Vidas: según tu decisión (§5).

### Fase 4 — Contenido nuevo del curso 1 (3-5 sesiones, la más larga)
- "Primeros pasos con TortuScript": 8 secciones × 4-5 lecciones × ~8 pasos, reescrito
  en formato Mimo (los 30 ejercicios actuales pasan a ser el "desafío" de cada lección).
- Curso "Dibujá con la tortuga" (lo más motivador para 10-12 años).
- Puente final "De TortuScript a Python real".
- Todo pasa por el validador de la Fase 0.

### Fase 5 — Repaso espaciado y práctica (1-2 sesiones)
- "Práctica del día" con pasos de lecciones viejas elegidos por olvido (repetición espaciada)
  e intercalados (interleaving).

### Fase 6 — Playground guardable, proyectos guiados y certificado (2 sesiones)
- "Mis proyectos": guardar, abrir, duplicar lo hecho en Experimentar y Tortuga.
- 3 proyectos guiados: adivinador de números, calculadora, dibujo de una casa con la tortuga.
- Certificado imprimible (HTML/PDF) al terminar un curso, **gratis**.

### Fase 7 — Estética y accesibilidad (2-3 sesiones, según decisión técnica)
- Sistema de diseño propio (tokens de color, tipografía grande, tarjetas redondeadas,
  animaciones cortas, celebraciones).
- Accesibilidad: tamaño de letra ajustable, alto contraste, todo usable con teclado,
  audio opcional de las consignas (TTS local).

### Fase 8 — Empaquetado (1 sesión)
- Instalable para Linux (y Windows si hace falta) según la metodología del vault.

**Total estimado: 17-24 sesiones.** Orden recomendado: 0 → 1 → 2 → 4 (curso 1 mínimo) →
3 → 5 → 6 → 7 → 8. La estética (7) puede adelantarse si elegís cambiar de tecnología de
interfaz, porque conviene hacerlo antes de construir muchas pantallas.

## 5. Decisiones que necesito de vos antes de empezar

| # | Decisión | Opciones | Mi recomendación |
|---|---|---|---|
| 1 | **Tecnología de interfaz** | a) Tk puro (0 dependencias, limitado) · b) **CustomTkinter** (1 dependencia, es el estándar de tu vault, redondeado y moderno) · c) Web local (HTML/JS en el navegador, lo más parecido a Mimo, cambio grande) | **b**, auditada con dependency-auditor |
| 2 | **Vidas** | a) Como Mimo (se pierden, se recargan) · b) **Sin vidas: ante un error, pista y reintento** · c) Opcionales, apagadas por defecto | **b**: con 10 años castigan más de lo que enseñan |
| 3 | **Liga** | a) **Local entre perfiles + rivales simulados** · b) Sin liga | **a** |
| 4 | **Registro de lenguaje** | a) **Voseo rioplatense** (como hoy) · b) Neutro | **a**, salvo que apunten a otros países |
| 5 | **Audio de consignas** | a) TTS local (espeak-ng/Piper, ya usado en Hanna) · b) Sin audio | **a**, en Fase 7 |
| 6 | **Alcance del curso 1** | a) **8 secciones** (~35 lecciones) · b) Empezar con 3 secciones y crecer | **b** si querés ver resultados antes |

## 6. Integración con lo que ya existe

- Se conservan: traductor (tokenize), ejecutor con sandbox, mensajes de error, progreso
  atómico con perfiles, tortuga con depurador, Referencia, Repaso y tests (51).
- El progreso actual se migra: los ejercicios completados cuentan como lecciones completadas.
- La ventana de Ejercicios actual se convierte en el tipo de paso "Escribir código".

## 7. Riesgos

| Riesgo | Mitigación |
|---|---|
| Escribir contenido lleva mucho más que programar | Validador (Fase 0) + plantillas; empezar con 3 secciones |
| Tk no alcanza para la estética deseada | Decisión 1 antes de la Fase 2 |
| Gamificación que genere ansiedad | Vidas apagadas, racha con congelador ganado, sin rankings públicos |
| Clonar de más (derechos) | Solo mecánicas; contenido y arte propios |

## 8. Fuentes

- [mimo.org](https://mimo.org/) · [Planes (mimo.org/pro)](https://mimo.org/pro) ·
  [Cuánto cuesta Mimo (blog oficial)](https://mimo.org/blog/how-much-does-mimo-cost-is-it-worth-it)
- [Leaderboard](https://support.mimo.org/hc/en-us/articles/24330086777874-What-is-the-Mimo-Leaderboard-and-how-does-it-work) ·
  [Streak Freeze](https://support.mimo.org/hc/en-us/articles/360017480999-How-does-the-Streak-Freeze-work) ·
  [Streak Challenge](https://support.mimo.org/hc/en-us/articles/25873385070098-How-Streak-Challenge-works) (fragmentos vía buscador; el sitio bloquea la lectura directa)
- [Common Sense Media](https://www.commonsensemedia.org/app-reviews/mimo-learn-how-to-code-through-interactive-tutorials-and-quizzes) ·
  [Educational App Store](https://www.educationalappstore.com/app/mimo-learn-to-code) ·
  [Career Karma](https://careerkarma.com/blog/mimo-coding-app-review/) ·
  [Coddy](https://coddy.tech/vs/mimo) · [ScreensDesign (UI)](https://screensdesign.com/showcase/mimo-learn-codingprogramming)
