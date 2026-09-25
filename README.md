# 🐢 TortuScript → Python

Una aplicación para que chicos de 10 a 14 años aprendan a programar en Python usando **TortuScript**, un pseudolenguaje en español que se traduce solo a Python real. Se usa en el navegador, **corre en tu compu** (sin internet, sin cuentas y sin anuncios) y se parece a las apps de lecciones cortas: explicación, práctica, feedback al instante, racha, logros y una liga de amigos.

```
# TortuScript               →     Python
mostrar "Hola mundo"        →     print("Hola mundo")
nombre es "Juan"            →     nombre = "Juan"
si edad > 10:               →     if edad > 10:
    mostrar "Grande"        →         print("Grande")
repetir 3 veces:            →     for _ in range(3):
    mostrar "Hola"          →         print("Hola")
funcion saludar(n):         →     def saludar(n):
    mostrar n               →         print(n)
```

---

## Cómo se usa

**Requisitos:** Python 3.9 o más nuevo. Nada más: la única dependencia es Flask.

```bash
python -m venv .venv                          # una sola vez
.venv/bin/python -m pip install -r requirements.txt     # en Windows: .venv\Scripts\python.exe
.venv/bin/python iniciar_web.py               # abre el navegador solo
```

También podés hacer doble clic en `lanzadores/Iniciar TortuScript.bat` (Windows) o correr `lanzadores/iniciar_tortuscript.sh` (Linux/macOS). Para tener un acceso directo: `lanzadores/crear_acceso_windows.ps1` o `sh lanzadores/instalar_acceso_linux.sh`.

Opciones de `iniciar_web.py`: `--sin-navegador` (solo arranca el servidor) y `--puerto N`. Se cierra con Ctrl+C o cerrando la ventana.

Si la red de tu oficina o escuela intercepta certificados SSL y `pip` falla, apuntá `PIP_CERT` al bundle de certificados de tu sistema.

---

## Qué hay adentro

### 🗺️ Aprender: cuatro cursos, 51 lecciones
Cada lección dura unos 2 minutos y sigue el ciclo **explicar → practicar → escribir**: una tarjeta que explica con un ejemplo que se puede ejecutar, preguntas de elegir, predecir lo que muestra un programa, completar con fichas, ordenar líneas y, al final, escribir el programa. Ante un error hay una pista específica; se puede reintentar y, tras dos errores, ver la respuesta (sin XP en ese paso). **No hay vidas ni castigos.**

| Curso | Lecciones | De qué trata |
|---|---|---|
| 🐢 Primeros pasos con TortuScript | 30 | mostrar, variables, preguntar, cuentas, si/sino, repetir, mientras, funciones |
| 🎨 Dibujá con la tortuga | 12 | avanzar y girar, figuras con repetir, colores, lápiz, variables y funciones (se abre al terminar *Dos variables*) |
| 🛠️ Proyectos guiados | 3 | un adivinador de números, una calculadora y una casa; cada paso sigue desde el código anterior |
| 🐍 De TortuScript a Python real | 6 | print, input, if, for/while y def, escritos en Python de verdad (se abre al terminar *Desafío final*) |

El **camino** es la pantalla de inicio: muestra dónde estás y qué sigue. Las lecciones se desbloquean en orden.

### 🎮 Motivación, sin presión
- **XP y niveles** (10 títulos: 🐣 Aprendiz … 🏆 Maestro). Solo suma cuando mejorás tu mejor resultado.
- **Meta diaria** con anillo: 5, 10 o 15 minutos (20, 40 o 60 XP).
- **Racha** con **congeladores que se ganan** (uno cada 7 días seguidos, hasta 2): si faltás un día, la racha se salva sola. Reto de 7 días.
- **25 logros** que nunca se pierden y una **liga local semanal** (Bronce → Diamante) entre los perfiles de la compu y rivales simulados; suben los 3 primeros y nadie baja.
- **Práctica del día**: repaso espaciado e intercalado (1, 2, 4, 8 y 16 días) con los pasos de lecciones viejas.
- **Certificado imprimible** (o PDF) al terminar cada curso.

### 🧰 Herramientas
- **🧪 Experimentar**: escribís lo que quieras, con la traducción a Python en vivo. Acepta TortuScript o Python.
- **🎨 Zona Tortuga**: dibujo con `avanzar`, `retroceder`, `girar_der`, `girar_izq`, `color`, `subir_lapiz` y `bajar_lapiz`; con *paso a paso* se resalta cada línea mientras la tortuga la ejecuta. Colores en español (`"rojo"`, `"celeste"`...) o `#rrggbb`.
- **📂 Mis proyectos**: guardar, abrir, duplicar y borrar lo hecho en Experimentar y en la Zona Tortuga (hasta 30 por perfil).
- **📖 Referencia** del lenguaje, **🗺️ Mapa** de los 30 ejercicios clásicos, **🔁 Repaso** de ejercicios (4 modos) y **📊 Resumen** de hoy.
- **👤 Perfiles**: cada chico tiene su progreso, sus ajustes y su meta en la misma compu.

### ♿ Accesibilidad y voz
Ajustes por perfil (⚙️): tamaño de letra grande y enorme, alto contraste, tipo de letra fácil de leer, menos movimiento y **lectura en voz alta** de las consignas (usa las voces del sistema, sin internet). Se maneja todo con el teclado (enlace *Saltar al contenido*, foco visible, `Esc` sale del editor, teclas `1`–`9` eligen opciones) y funciona con lectores de pantalla. El contraste de las páginas principales cumple WCAG AA (`herramientas/revisar_contraste.py`).

---

## El lenguaje TortuScript

| TortuScript | Python | Descripción |
|-------------|--------|-------------|
| `mostrar X` | `print(X)` | Mostrar en pantalla (`mostrar "a", 3` junta varias cosas) |
| `X es Y` | `X = Y` | Asignar variable (dentro de una condición, `es` compara) |
| `preguntar("msg")` | `input("msg")` | Pedir un dato |
| `si` / `sino si` / `sino` | `if` / `elif` / `else` | Condicionales |
| `repetir N veces:` | `for _ in range(N):` | Repetir |
| `para x en lista:` | `for x in lista:` | Recorrer una lista |
| `mientras cond:` | `while cond:` | Repetir mientras se cumpla |
| `funcion n(p):` / `devolver X` | `def n(p):` / `return X` | Funciones |
| `y` / `o` / `no` | `and` / `or` / `not` | Lógica |
| `Verdadero` / `Falso` | `True` / `False` | Booleanos |

Las palabras aceptan **tildes y mayúsculas** (`función`, `Mostrar`). `y`, `o`, `no` y `color` solo se traducen cuando funcionan como operador o comando: se pueden usar como nombres de variable. La indentación puede ser con espacios o con Tab.

---

## Cómo está hecho

```
proyecto/
├── iniciar_web.py            ← lanzador (abre el navegador)
├── lanzadores/               ← .bat / .sh / accesos directos
├── requirements.txt          ← Flask
├── tortuscript/              ← NÚCLEO sin interfaz
│   ├── translator.py         ← TortuScript → Python (con tokenize)
│   ├── executor.py           ← ejecuta el código del chico con protecciones
│   ├── worker.py, proceso.py ← el código corre en un subproceso con límites
│   ├── error_handler.py      ← errores explicados en lenguaje simple
│   ├── evaluacion.py         ← compara salidas y dibujos con la solución
│   ├── tortuga.py            ← la tortuga como registro de órdenes + comparación de dibujos
│   ├── leccion.py            ← motor de lecciones (pasos, comprobación, camino, cursos)
│   ├── practica.py           ← repaso espaciado
│   ├── logros.py, liga.py    ← gamificación
│   ├── proyectos.py          ← Mis proyectos
│   ├── progreso.py           ← XP, racha, perfiles, ajustes (guardado seguro)
│   ├── contenido.py, referencia.py, validacion.py
├── contenido/                ← los cursos y la referencia, como DATOS (JSON)
├── web/                      ← Flask: app.py, templates/, static/{css,js,vendor,fonts,img}
├── herramientas/             ← validador de contenido, jugador de cursos, contraste, paquete
├── tests/                    ← unittest
└── docs/                     ← ADR, roadmap, guía para escribir cursos
```

- **El contenido es dato, no código.** Los cursos están en `contenido/cursos/*.json` y los revisa un **validador automático** que corre cada respuesta, cada fragmento y cada salida esperada: nunca llega a la pantalla un ejercicio roto. Guía completa en [`docs/CONTENIDO.md`](docs/CONTENIDO.md).
- **Un solo servidor local.** Flask escucha solo en `127.0.0.1`; toda la API exige un token secreto de la sesión (una página ajena abierta en el navegador no puede usarla) y se rechazan `Host` que no sean locales.
- **El código del chico nunca corre dentro del servidor.** Va a un subproceso con límite de tiempo y de memoria (512 MB: `resource` en Linux/macOS, un Job Object en Windows; el de CPU es solo Linux/macOS), validación previa con AST (sin `import` ni nombres que empiecen con `_`), builtins limitados, tope de 50.000 pasos y de 20.000 caracteres de salida. **No es un sandbox para código hostil**: protege al chico de errores y de copiar/pegar cosas peligrosas.
- **`preguntar()`** se resuelve re-ejecutando el programa con las respuestas acumuladas; la tortuga es un registro de órdenes que el navegador anima en un `<canvas>`.
- **Todo offline**: CodeMirror, confeti y las fuentes están en `web/static/`; no se pide nada a internet.

Decisiones de diseño: [`docs/decisions/`](docs/decisions/) (ADR-001 migración a web, ADR-002 cursos como datos y progreso aditivo).

---

## Dónde se guarda el progreso

En `progreso_<perfil>.json`, junto al programa (el perfil inicial es `default`). Cada guardado es atómico y deja una copia `.bak`; si el archivo se daña se aparta como `.corrupto-<fecha>` y se recupera desde la copia: nunca se pisa en silencio. El esquema es **aditivo**: los archivos de versiones anteriores se abren y se completan solos (hoy es la versión 8). Para empezar de cero un perfil, borrá su `progreso_<perfil>.json` (y el `.bak`).

Los logs de errores internos van a `logs/tortuscript.log` y nunca se muestran al chico.

---

## Para quien mantiene el proyecto

```bash
python -m unittest discover tests            # tests (325)
python herramientas/validar_contenido.py     # valida todos los cursos
python herramientas/crear_paquete.py         # arma dist/TortuScript-<fecha>.zip para instalar en otra compu
```

Con **Playwright** (opcional, no está en `requirements.txt`) se puede verificar la interfaz real:

```bash
python herramientas/servidor_de_prueba.py    # servidor con progreso temporal (otra terminal)
python herramientas/jugar_cursos.py          # juega TODAS las lecciones por el navegador
python herramientas/revisar_contraste.py     # contraste WCAG AA en modo normal y alto contraste
python herramientas/revisar_responsive.py    # que nada se desborde en pantallas de 320 a 768 px
```

Cambios recientes: [`CHANGELOG.md`](CHANGELOG.md). Roadmap: [`docs/ROADMAP_MIMO_KIDS.md`](docs/ROADMAP_MIMO_KIDS.md).

*Hecho con 🐢 y mucho amor para aprender a programar de a poco.*
