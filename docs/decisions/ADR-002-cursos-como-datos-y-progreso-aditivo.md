# ADR-002: Cursos como datos, motor de lecciones y progreso aditivo

## Estado: Aceptado (25/09/2026) — implementado en las fases F3 a F8 de la migración a web

## Contexto
- La app Tk tenía 30 ejercicios "escribí un programa entero" y el contenido estaba en código Python.
  Cada ejercicio nuevo se probaba a mano, uno por uno.
- El roadmap "Mimo para chicos" pide lecciones cortas con varios tipos de paso, cursos nuevos
  (tortuga, proyectos, Python real), gamificación y accesibilidad: más de 250 pasos de contenido.
- Había progreso guardado de chicos reales (`progreso_<perfil>.json`) que no se podía perder.

## Decisiones

### 1. El contenido es dato y se valida solo
Los cursos viven en `contenido/cursos/*.json` (curso → sección → lección → paso) con 6 tipos de
paso. `tortuscript/validacion.py` ejecuta cada respuesta, fragmento y salida esperada, comprueba
que las opciones incorrectas no sean correctas, que las palabras se enseñen antes de usarse y que
el Python mostrado lado a lado sea la traducción exacta. Corre dentro de los tests.
Guía: `docs/CONTENIDO.md`.

### 2. El motor es lógica pura; la interfaz solo dibuja
`tortuscript/leccion.py` decide qué ve el chico (`paso_publico`, que **nunca** incluye la
respuesta), cómo se comprueba cada tipo (`comprobar`) y cuánto vale. El servidor cuenta los
errores por paso (no se puede pedir la respuesta sin intentar) y el navegador solo muestra.
Los pasos de `completar` y `ordenar` aceptan otra solución si muestra (o dibuja) lo mismo: se
comprueba ejecutando.

### 3. La tortuga es un registro de órdenes
El servidor no dibuja: anota cada orden con su línea y el navegador las anima en un `<canvas>`
(depurador paso a paso incluido). Dos dibujos se comparan como conjuntos de celdas de 3×3 con su
color (parecido ≥ 0,97): no importa el orden, el sentido ni cuántos `avanzar` se usen.

### 4. El progreso solo crece (esquema aditivo, versionado)
Cada versión (v2 a v8) **agrega** campos con valores por defecto y `_migrar` completa los que
faltan; nada se renombra ni se borra. La clave histórica `ejercicios` (índice de los 30
`escribir` del curso 1) sigue siendo la fuente de verdad para esos ejercicios, y una lección del
curso 1 cuenta como completada si sus `escribir` ya estaban resueltos: el avance anterior al
motor de lecciones se conserva. Los perfiles nuevos pasan por la bienvenida; los que ya tenían
avance, no.

### 5. Cursos que se abren y lecciones que piden otras
`requiere` a nivel de curso o de lección. El camino nunca se saltea una lección: la primera
pendiente es "la que toca" y las siguientes esperan.

### 6. Gamificación amable
Sin vidas ni compras (decisión de producto): errores con pista y reintento; los congeladores de
racha **se ganan** (uno cada 7 días, hasta 2); los logros no se pierden; la liga es local (perfiles
de la PC + rivales simulados deterministas por semana) y nadie baja. No hay bonus de XP por
lección para no inflar los niveles: los umbrales se calibran con `xp_maximo` del curso 1.

### 7. Accesibilidad por perfil, aplicada desde el servidor
Los ajustes (letra, contraste, movimiento, tipografía, voz) se guardan en el perfil y el servidor
los escribe como atributos `data-*` del `<html>`: sin parpadeo y sin depender de `localStorage`.
La voz usa Web Speech con las voces del sistema.

## Alternativas descartadas
- **Pyodide** (Python en el navegador): pesado (10–20 MB), obligaba a rehacer el sandbox y los
  mensajes de error; el subproceso del servidor da además límites de tiempo y memoria.
- **Framework JS con build**: agrega Node y una cadena de compilación; HTML + CSS + JS simples se
  editan y se recargan.
- **TTS con Piper/espeak-ng**: una dependencia y un binario por sistema; Web Speech ya viene con
  el navegador y las voces del sistema.
- **Migrar a un esquema nuevo de progreso**: riesgo de perder avance; un esquema aditivo no
  necesita migración destructiva.

## Consecuencias
+ Sumar una lección es escribir JSON y correr el validador; nunca llega un ejercicio roto.
+ Los tests cubren el motor sin abrir un navegador; el jugador de cursos (Playwright) verifica la
  interfaz real de punta a punta.
+ El progreso de los chicos existentes sigue funcionando en cada versión.
− `contenido/` y `web/` comparten reglas (banderas de paso) que hay que mantener sincronizadas
  con el motor (`paso_publico`); los tests de contenido y el jugador lo detectan.
− Los ids de lección forman parte del progreso: renombrarlos borra ese avance.
− La comparación de dibujos es estricta con los ángulos (por diseño: 89° ≠ 90°).
