# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Todavía no hay una
versión publicada de la app web: los cambios de versión se consultan antes de fijarlos.

## Sin publicar — color de la tortuga por nivel (26/09/2026)

Rama `feat/color-por-nivel`.

### Agregado
- **La tortuga cambia de color al subir de nivel** (niveles de XP 1–10: verde, turquesa, azul, violeta, fucsia, rojo,
  naranja, dorado, marrón y negro). Todos contrastan al menos 3:1 con el fondo blanco del lienzo, y el nivel 1 es el
  verde de siempre. El color se actualiza en el momento en que se sube de nivel.

### Cambiado
- El **cuerpo** de la tortuga ya no toma el color del lápiz: muestra el progreso del chico. El **lápiz** arranca siempre
  en verde y solo cambia con `color`, así que los dibujos que se comparan en los ejercicios no se ven afectados.

## Sin publicar — migración a aplicación web (25/09/2026)

Rama `feature/migracion-web-paridad`. Fases F0 a F9 del roadmap (`docs/ROADMAP_MIMO_KIDS.md`).

### Agregado
- **App web local** (Flask + HTML/CSS/JS, sin build, todo offline) con paridad completa con la app
  de escritorio: ejercicios, Experimentar, Zona Tortuga con canvas y depurador paso a paso, Mapa,
  Resumen, Repaso (4 modos), Referencia, perfiles, sonidos y confeti.
- **Motor de lecciones** con 6 tipos de paso (explicación, elegir, predecir, completar con fichas,
  ordenar y escribir), feedback por paso, pista específica, "ver respuesta" tras 2 errores y
  progreso por lección.
- **Cuatro cursos, 51 lecciones, 291 pasos**: Primeros pasos (30), Dibujá con la tortuga (12),
  Proyectos guiados (3) y De TortuScript a Python real (6). Los cursos se abren al terminar una
  lección de otro curso; las lecciones pueden pedir otra.
- **Camino** como pantalla de inicio, **onboarding** de 3 pasos y **meta diaria** con anillo.
- **Gamificación amable**: racha con congeladores que se ganan, reto de 7 días, 25 logros, liga
  semanal local con rivales simulados, práctica del día (repaso espaciado e intercalado).
- **Mis proyectos** (guardar, abrir, duplicar, borrar) y **certificado imprimible** por curso.
- **Accesibilidad**: tamaño de letra, alto contraste, letra fácil de leer, menos movimiento,
  teclado completo, lectores de pantalla y lectura en voz alta de las consignas.
- Validador automático de contenido (`herramientas/validar_contenido.py`) integrado a los tests.
- Herramientas opcionales con Playwright: jugador de cursos, revisor de contraste y servidor de
  prueba. `herramientas/crear_paquete.py` arma un `.zip` instalable.
- Lanzador `iniciar_web.py` y accesos directos para Windows y Linux; ícono.
- Documentación: `docs/CONTENIDO.md`, ADR-001 (migración) y ADR-002 (cursos como datos).

### Cambiado
- Pantallas chicas: el encabezado se compacta con un botón **Menú** y ninguna página se desborda en 320–768 px
  (`herramientas/revisar_responsive.py`). El servidor usa conexiones HTTP/1.1 que se reusan.
- **Límite de memoria** del subproceso también en Windows (Job Object vía `ctypes`, sin dependencias): una bomba de
  memoria termina con un mensaje claro en vez de congelar la compu. Los pedidos web van de a uno para que el
  progreso no se pise entre pestañas.
- El código del chico corre en un **subproceso** con límites (antes, dentro de la app).
- Los niveles se recalibraron (80/180/300/440/600/780/980/1200/1350 XP) porque el XP máximo pasó
  de 900 a 1460. El XP guardado no cambia.
- El progreso pasó del esquema 2 al 8, **siempre agregando campos**: los archivos anteriores
  siguen abriéndose y se completan solos.
- El límite de tiempo del subproceso es de 10 s (un antivirus puede demorar el arranque de Python).

### Corregido
- El worker escribía su JSON en cp1252 en Windows y fallaba con emojis en cualquier mensaje de error.
- Dos diferencias de Python 3.9 (comillas sin cerrar en el traductor y `:` faltante en el mensaje
  de error).
- Chips y botones con texto oscuro sobre fondo oscuro y botones violetas con poco contraste.

### Eliminado
- La app de escritorio Tkinter: `ui/`, `main.py`, `highlighter.py`, `celebracion.py`,
  `dialogo_preguntar.py`, `sounds.py` y `utils.py`, además del parámetro `pedir_entrada` del ejecutor.
