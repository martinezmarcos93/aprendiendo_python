# ADR-001: Migrar TortuScript de Tkinter a una aplicación web local (Flask)

## Estado: Aceptado (decisión de Marcos, 24/09/2026) — detalles técnicos: propuestos, a confirmar

## Contexto
- La interfaz Tkinter no permite la estética que buscamos (modelo: Mimo): tarjetas
  redondeadas, animaciones, tipografías, transiciones, celebraciones. Además trae problemas
  propios del escritorio en Linux: layout que se recorta, rueda del mouse, IBus que se traga
  el Intro numérico, diálogos que no respetan el estilo.
- El roadmap "Mimo para chicos" (docs/ROADMAP_MIMO_KIDS.md) fue aprobado. Construir sus
  pantallas en Tk para después tirarlas sería trabajo doble.
- El núcleo ya es casi independiente de la interfaz: traductor (tokenize), ejecutor con
  sandbox, mensajes de error y progreso atómico, con 51 tests. El único acople con Tk es que
  el ejecutor abre el diálogo de `preguntar()`.

## Decisión
Reconstruir TortuScript como **aplicación web local**: servidor **Flask** en
`127.0.0.1` (sin internet, sin cuentas) que abre el navegador; interfaz en **HTML + CSS +
JavaScript**. El núcleo Python se conserva y se separa como paquete. La app Tk sigue
funcionando hasta alcanzar la paridad y entonces se elimina (patrón *strangler*).

## Propuestas técnicas (a confirmar)

### 1. Dónde corre el código del chico → **en el servidor, en un subproceso**
| Opción | + | − |
|---|---|---|
| **Servidor, subproceso por ejecución** ✅ | Reusa traductor, sandbox y mensajes; timeout real y **límite de memoria** (resuelve lo pendiente E3); aislado del servidor | `preguntar()` necesita una técnica (abajo) |
| Navegador con Pyodide (Python en WebAssembly) | `input()` nativo, todo en el cliente | ~10-20 MB, rehacer sandbox y mensajes, arranque lento |

**`preguntar()` en la web**: se ejecuta el programa; si llega a un `preguntar` sin
respuesta, el subproceso se detiene y devuelve la pregunta; la página muestra un modal con
el estilo de la app; al responder, se re-ejecuta desde el principio con las respuestas
acumuladas (el mismo mecanismo `entradas_fijas` que ya usa la evaluación). Los programas de
los chicos son deterministas (no hay `random`), así que es invisible.

**Tortuga en la web**: el servidor no dibuja; registra la lista de órdenes (avanzar,
girar, color…) con el número de línea de cada una, y el navegador las anima en un
`<canvas>`, resaltando la línea (depurador paso a paso) sin demoras en el servidor.

### 2. Interfaz → **HTML + CSS + JavaScript sin framework ni build**
- Sin Node ni compilación: se edita y se recarga. CSS con variables (tema claro/oscuro,
  alto contraste), animaciones CSS.
- Editor de código: **CodeMirror** (MIT) guardado en `static/vendor/` con un modo de
  resaltado para TortuScript. Fuentes con licencia libre (OFL) también locales.
- **Todo offline**: nada desde CDN.

### 3. Estructura → **mismo repo, reorganizado**
```
python-para-ninos/
├── tortuscript/            # núcleo (sin interfaz): traductor, ejecutor, errores,
│   │                       #   progreso, contenido, evaluación, tortuga (registro)
├── contenido/cursos/*.json # lecciones como datos (Fase 0 del roadmap)
├── web/
│   ├── app.py              # Flask: páginas + API JSON
│   ├── templates/          # base.html, camino, lección, playground, tortuga…
│   └── static/{css,js,vendor,fonts,img}/
├── herramientas/validar_contenido.py
├── tests/
└── ui/ (Tk, se elimina al llegar a paridad)
```

### Dependencias nuevas
- **Flask** (BSD-3, madura, estándar del vault). Pasa por dependency-auditor antes de instalarse.
- Front: CodeMirror (MIT), canvas-confetti (ISC) opcional. Guardados localmente.

## Consecuencias
+ Estética moderna y animaciones reales; mismo código de UI en Linux, Windows y macOS.
+ Se reusa el núcleo probado; el subproceso agrega límite de memoria y aislamiento.
+ Camino natural a futuro: tablet o celular en la red de casa, o publicar.
− Dos procesos (servidor + navegador) en vez de uno; hay que "abrir" la app con un lanzador.
− Una dependencia (Flask) donde antes había cero.
− Hasta la paridad conviven dos interfaces.
