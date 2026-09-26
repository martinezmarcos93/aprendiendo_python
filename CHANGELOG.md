# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Todavía no hay una
versión publicada de la app web: los cambios de versión se consultan antes de fijarlos.

## Sin publicar — cierre de lección reforzado (26/09/2026)

Rama `feat/cierre-de-leccion`.

### Agregado
- Al terminar una lección, la pantalla final cuenta **qué aprendí → qué gané → qué sigue**: las palabras que la lección
  presentó por primera vez (📚 *Aprendiste*), las que se usaron para practicar (🔁 *Practicaste*), el XP y los aciertos, y
  el botón **▶ Sigue: <próxima lección>**.
- Las palabras salen del propio contenido, con la misma regla del validador (una palabra se "aprende" donde aparece por
  primera vez en una *Forma* o un ejemplo, recorriendo los cursos en orden). En *Python real* se usan sus
  `palabras_pista`. Ningún campo nuevo en los JSON.

### Cambiado
- `translator.palabras_usadas()` concentra el cálculo de palabras que antes estaba solo en el validador.
- README: coma mal puesta en la lista de herramientas.

## Sin publicar — página de ayuda (26/09/2026)

Rama `feat/ayuda`.

### Agregado
- **❓ Ayuda** (menú *Más*): 10 preguntas frecuentes con respuestas cortas, distinta de la Referencia del lenguaje.
  Cómo empezar, si hay que guardar, varios chicos en la misma compu, cómo pasar el progreso a otra compu, qué pasa si
  te equivocás, la racha, la accesibilidad, dónde ver cómo se escribe algo, qué hacer si algo no anda (el código de
  referencia y el log) y si hace falta internet.
- La ayuda es dato (`contenido/ayuda.json`) y un test le aplica las mismas reglas de estilo que a los cursos.
- No guarda reportes ni opiniones: eso es feedback local y depende de ADR-005, que sigue en Propuesta.

## Sin publicar — pantalla de retorno (26/09/2026)

Rama `feat/pantalla-de-retorno`.

### Agregado
- **Al volver un día nuevo**, el inicio saluda "¡Hola de nuevo!" y cuenta qué pasó la última vez y qué sigue:
  "Ayer ganaste 40 XP. Hoy te espera «Dos líneas». Y tenés 3 tarjetas para repasar", con el botón **▶ Continuar**.
  Solo cuenta lo bueno: si faltó varios días, no lo reta. Usa datos que el progreso ya guardaba (sin cambio de esquema).

## Sin publicar — exportar e importar el progreso (26/09/2026)

Rama `feat/exportar-importar`.

### Agregado
- **Guardar el progreso en un archivo y traerlo en otra compu**, desde el modal de perfiles (👤). El archivo
  (`tortuscript-<perfil>-<fecha>.json`) lleva el progreso completo: lecciones, XP, logros, ajustes y proyectos.
- **Importar nunca pisa nada**: crea un perfil nuevo (`lua`, o `lua_2` si ya existe) y cambia a ese perfil.
- El archivo importado se valida como entrada de afuera (`tortuscript/respaldo.py`): formato y versión, tipo de cada
  campo, sin números negativos, meta/experiencia/ajustes válidos, proyectos con las mismas reglas que al guardarlos,
  tope de 1 MB y nombre de perfil saneado. Los campos desconocidos se descartan.

## Sin publicar — páginas de error humanas (26/09/2026)

Rama `feat/pagina-de-error`.

### Agregado
- **Páginas de error propias** para 400, 403, 404 y 500, en lenguaje para chicos y con un botón para volver al inicio,
  en vez de las páginas genéricas en inglés de Flask. En la API, el mismo mensaje en JSON (`error`, `mensaje`).
- Un error interno muestra "Algo se rompió de nuestro lado... Tu progreso sigue guardado" y un **código de referencia**
  (p. ej. `8F72A1`) que queda en `logs/tortuscript.log` junto con la traza. Nunca se muestran trazas ni rutas.
- La página de error no depende del progreso: se muestra aunque lo que falló sea cargarlo.

## Sin publicar — cabeceras de seguridad y CSP (26/09/2026)

Rama `feat/security-headers`. Era el único punto en FAIL de la auditoría de seguridad
(`docs/experimental/SEGURIDAD_SITIO_PROFESIONAL.md` §22).

### Agregado
- **Cabeceras de seguridad en toda respuesta** (páginas, API, estáticos y errores): Content-Security-Policy,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Permissions-Policy`,
  `Cross-Origin-Opener-Policy` y `Cross-Origin-Resource-Policy`.
- La CSP solo permite scripts propios (`script-src 'self'`: nada inline, nada de `eval`, nada de afuera) y ninguna
  página se puede meter en un marco. Los estilos inline siguen permitidos porque las plantillas usan `style=`.
- Un test recorre todas las plantillas y páginas y falla si vuelve a aparecer un script inline.

### Cambiado
- El token de la sesión y los avisos viajan como dato JSON (`#tortu-config`), no como script inline. El botón de
  imprimir del certificado y la lista de *Mis proyectos* se inician desde sus `.js`.
- El confeti se dibuja sin Worker (antes lo creaba desde `blob:`), así la CSP no necesita abrir `blob:`.

## Sin publicar — color de la tortuga por nivel (26/09/2026)

Rama `feat/color-por-nivel`.

### Agregado
- **La tortuga cambia de color al subir de nivel** (niveles de XP 1–10: verde, turquesa, azul, violeta, fucsia, rojo,
  naranja, dorado, marrón y negro). Todos contrastan al menos 3:1 con el fondo blanco del lienzo, y el nivel 1 es el
  verde de siempre. El color se actualiza en el momento en que se sube de nivel.

### Cambiado
- El **cuerpo** de la tortuga ya no toma el color del lápiz: muestra el progreso del chico. El **lápiz** arranca siempre
  en verde y solo cambia con `color`, así que los dibujos que se comparan en los ejercicios no se ven afectados.

## Sin publicar — laberintos de la tortuga (26/09/2026)

Rama `feat/laberinto`.

### Agregado
- **Tres laberintos** al final de *Dibujá con la tortuga* (lecciones 13–15): recto y con giros, más giros, y una
  escalera que exige `repetir`. El curso pasa a 15 lecciones (54 en total).
- **Nueva forma de comprobar** los pasos `escribir` con `laberinto`: no se compara con un dibujo, se revisan las reglas
  del mundo (no tocar paredes y terminar en la 🏁). Vale cualquier ruta. Si la tortuga choca, se frena contra la pared
  y el chico ve la línea que la hizo chocar, marcada en el editor. `usar` exige palabras (p. ej. `repetir`).
- El validador revisa el dato del laberinto y que la solución oficial llegue sin chocar y use lo que pide `usar`.

### Cambiado
- El paso final de *12. Reto: la espiral* ya no dice "¡Terminaste!": anuncia los laberintos. El cierre del curso pasó
  al final de *15. Laberinto III*. No se borró ni se movió ningún paso, así que el progreso guardado no cambia.

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
