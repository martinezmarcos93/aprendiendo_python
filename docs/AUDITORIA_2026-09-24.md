# Auditoría TortuScript → Python — 24/09/2026

> Alcance: los 20 archivos `.py` + `README.md` (2829 líneas), leídos completos. No existe el
> archivo "🐢 TortuScript → Python.txt" en el disco: se usó el `README.md` como especificación
> (tiene el mismo título). **Cada bug marcado ✔ se reprodujo ejecutando el código real**
> (Python 3.12.3, Ubuntu 24.04). No se modificó código: esto es solo el informe.


## 0. Estado de aplicación (rama `fix/auditoria-20260924`)

Aplicado con OK de Marcos (traductor: reescritura con `tokenize`). 45 tests en verde
(`python -m unittest discover tests`) + prueba de todas las ventanas sin errores de Tk.

| Resuelto | Pendiente (no aplicado) |
|---|---|
| **Traductor** T1–T10 (reescrito con tokenize) | E3 tope de **memoria** (requiere ejecutar en subproceso) |
| **Ejecutor** E1 depurador, E2 sandbox AST, E3 tope de salida, E4 límite global, E5 sin trazar tkinter | E6 `sys.stdout` global, E7 `SystemExit` (bajo impacto) |
| **Evaluación** X1, X2, X3, X4, X5, X6, X8 | X7 curva de dificultad y ejercicios nuevos (roadmap §8) |
| **Progreso** P1–P9 | U7 sonido en Linux/macOS |
| **Mensajes** U8 · **UI** U1–U6, U9, U12 | U10 confetti (código muerto), U11 `#` dentro de strings en el resaltado |
| README al día | Compatibilidad 3.8: revisada por lectura, **no probada** (no hay 3.8 instalado) |

---

## 1. Resumen ejecutivo

La base es buena: arquitectura simple y sin dependencias, todos los módulos importan, las 30
soluciones oficiales traducen a Python válido, 19/20 ejemplos de la Referencia coinciden
exactamente, el anti-bucle funciona y la UI tiene una estética cuidada. Pero hay **5 problemas
que rompen la experiencia del chico**:

1. **El traductor destruye variables comunes**: `y es 3` → `and = 3`. En la Zona Tortuga
   (coordenadas x/y) es casi inevitable. También `color es "rojo"` → `color(= "rojo")`. ✔
2. **Cualquier salida incorrecta cuenta como "completado"** (1⭐ + 5 XP) y desbloquea el
   siguiente ejercicio: el candado no protege nada. ✔
3. **El botón 🗺️ Mapa de la ventana de ejercicios tira `NameError`** (falta el import). ✔
4. **El depurador "Paso a paso" nunca resalta una línea** (activado por defecto, no hace nada). ✔
5. **El sandbox no es un sandbox**: el código del alumno llega a `os.system` en una línea. ✔

Además: el progreso puede **perderse en silencio**, los niveles 8-10 son **inalcanzables**, y
varias consignas de ejercicios **no coinciden con la salida exacta** que se exige.

## 2. Arquitectura real

```
main.py ─► ui/main_window.SistemaPrincipal (tk.Tk, selector de perfil)
            ├─ ui/ejercicios_window.VentanaEjercicios ─┬─ translator.TraductorTortuScript / detectar_tipo
            │     ▲ hereda                             ├─ executor.ejecutar_codigo ─► error_handler.explicar_error
            │  ui/repaso_window.VentanaRepaso          ├─ progreso (JSON por perfil, XP, racha, sesión)
            ├─ ui/experimentacion_window               ├─ celebracion.VentanaCelebracion ─► sounds
            ├─ ui/tortuga_window (turtle + depurador)  └─ highlighter.TortuHighlighter
            ├─ ui/mapa_window, ui/resumen_window, ui/referencia_window
            └─ utils.centrar_ventana (todas)
```

**Flujo de un intento:** editor → `detectar_tipo` (tortu/python/mixto) → `traducir_codigo`
(línea por línea, regex, sin estado entre líneas) → `ejecutar_codigo` (redirige `sys.stdout`,
`exec` con builtins recortados, `sys.settrace` como anti-bucle) → `_evaluar` **vuelve a traducir
y ejecutar la solución oficial** para obtener la salida esperada → compara `strip()` exacto →
estrellas según `pista_nivel` → `registrar_ejercicio` (XP solo si mejora, racha, sesión) →
`guardar_progreso` → celebración.

**Lo que está bien y conviene conservar:** evaluación por salida (no por código fuente),
globals frescos por ejecución, traducción 1:1 de líneas (los números de línea de los errores
coinciden con el código del chico), protección de strings en el traductor, XP que solo sube si
mejora, sin dependencias externas, compatible con Python 3.8 (sin `:=`, `match` ni tipos nuevos).

## 3. Bugs e inconsistencias

Severidad: 🔴 crítico · 🟠 alto · 🟡 medio · ⚪ bajo. ✔ = reproducido.

### 3.1 Traductor (`translator.py`)

| # | Sev | Línea | Problema | Reproducción |
|---|---|---|---|---|
| T1 | 🔴 ✔ | 17-19 | `y`/`o`/`no` se reemplazan como palabra suelta aunque sean **variables** | `y es 3` → `and = 3`; `si x > 3 y y < 2:` → `if x > 3 and and < 2:` |
| T2 | 🔴 ✔ | 30, 83-94 | `mostrar/avanzar/girar_*/color` se tratan como comando **en cualquier posición**, incluso como variable | `color es "rojo"` → `color(= "rojo")` |
| T3 | 🟠 ✔ | 72-77 | Solo preserva indentación con **espacios**: un Tab se descarta | `si Verdadero:` + `⇥mostrar` → `IndentationError` |
| T4 | 🟠 ✔ | 25, 97 | `es` siempre es asignación, también dentro de condiciones | `si edad es 10:` → `if edad = 10:` |
| T5 | 🟠 ✔ | 12 | `repetir` solo acepta un número literal | `repetir n veces:` queda sin traducir → `SyntaxError` |
| T6 | 🟠 ✔ | — | Sin tildes ni mayúsculas: chicos escriben `función`, `Mostrar`, `sí` | `función saludar():` → `SyntaxError` sin explicación útil |
| T7 | 🟡 ✔ | 13 | `para` → `for` pero `en` no → `in` (y la Referencia no documenta `para`) | `para i en range(3):` → `for i en range(3):` |
| T8 | 🟡 ✔ | 16 | No hay `sino si` (elif) | `sino si x > 3:` → `else if x > 3:` |
| T9 | 🟡 ✔ | 130-153 | `detectar_tipo` cuenta palabras **dentro de strings** | `print("hola es")` → "mixto" |
| T10 | ⚪ | — | Comentarios al final de línea también se "traducen" (inofensivo pero confuso en el panel Python) | `x es 1  # no cambiar` → `# not cambiar` |

### 3.2 Ejecutor (`executor.py`)

| # | Sev | Línea | Problema | Reproducción |
|---|---|---|---|---|
| E1 | 🔴 ✔ | 100-106 | El callback del depurador vive en la función de traza **global**, que solo recibe eventos `call`, nunca `line` | depurador recibe `[]` líneas; checkbox "Paso a paso" no hace nada |
| E2 | 🔴 ✔ | 55-82 | Sandbox evadible: `type` + atributos dunder permiten llegar a `os` | `[k for k in ().__class__.__base__.__subclasses__() if k.__name__=='_wrap_close'][0].__init__.__globals__['system']` |
| E3 | 🟠 ✔ | — | Sin límite de memoria ni de salida | `x = "a" * 10**9` se ejecuta (1 GB); un `print` gigante congela la UI |
| E4 | 🟡 | 106 | El presupuesto de 50.000 pasos es **por llamada**, no total (se crea un contador por frame) | un programa que llama muchas funciones cortas nunca corta |
| E5 | 🟡 | 30-48 | `input()` abre un diálogo modal mientras `settrace` está activo (traza también el código de tkinter) | lentitud al pedir datos |
| E6 | 🟡 | 92-94 | Redirige `sys.stdout` global (no thread-safe) y `extra_globals` puede pisar builtins | — |
| E7 | ⚪ | 121 | `except Exception`: no captura `SystemExit`/`KeyboardInterrupt` del código del chico (hoy no son alcanzables sin builtins, pero conviene cerrarlo) | — |

### 3.3 Evaluación y ejercicios (`ui/ejercicios_window.py`, `ejercicios.py`)

| # | Sev | Línea | Problema | Reproducción |
|---|---|---|---|---|
| X1 | 🔴 ✔ | 235-250 | Salida incorrecta ⇒ `registrar_ejercicio(…, 1, 5)` ⇒ `completado: True` ⇒ desbloquea el siguiente | escribir `mostrar "x"` en cualquier ejercicio y tocar "Siguiente" |
| X2 | 🔴 ✔ | 337-341 | `VentanaMapa` no está importada | botón 🗺️ Mapa dentro de Ejercicios → `NameError` |
| X3 | 🟠 | 211-212 | La solución oficial se **ejecuta** para calcular la salida esperada: en ejercicios 7-9 (`preguntar`) aparece **un segundo diálogo**, y si el chico escribe otra cosa, "no coincide" | ejercicio 7 |
| X4 | 🟠 | 323-328 | "Limpiar" reinicia `pista_nivel` | ver solución (pista 3) → Limpiar → pegar → 3⭐ |
| X5 | 🟠 ✔ | 295-298 | Pista 1 busca **subcadenas**: "Hola mundo" sugiere usar `o`; "Nombre" sugiere `no` y `es` | `_detectar_keywords` |
| X6 | 🟠 | ejercicios.py | Consignas que no coinciden con la salida exacta exigida: #3 "dos mensajes **distintos**" (exige Hola/Chau), #5 "tu nombre" (exige Juan), #26 "nombre dos veces" (exige `AnaAna` en una línea), #27 "varias veces" (exige 4), #18 "sumar números" (no dice cuáles) | cualquier solución válida distinta es rechazada |
| X7 | 🟡 | ejercicios.py | Curva: #25-#30 ("Desafíos", nivel 8) son `mostrar 100` y `mostrar 1 + 2`, más fáciles que el nivel 5. No hay ejercicios de `mientras`, `devolver`, `y/o/no`, `clase` ni tortuga, aunque la Referencia los enseña | — |
| X8 | ⚪ | 343-355 | En el último ejercicio "Siguiente" no hace nada ni felicita; cambiar de ejercicio borra el código sin avisar | — |

### 3.4 Progreso (`progreso.py`)

| # | Sev | Línea | Problema |
|---|---|---|---|
| P1 | 🔴 | 51-52, 61-62 | `except Exception: pass` en carga y guardado: si el JSON está corrupto se arranca de cero **y el próximo guardado pisa el archivo** → pérdida total sin aviso |
| P2 | 🟠 | 56-62 | Escritura no atómica (`open("w")`): un corte a mitad deja JSON truncado → P1 |
| P3 | 🟠 | 12-13 + main_window 76-84 | Perfil global mutable: con Ejercicios abierto como A, cambiar a B y completar → **los datos de A se escriben en el archivo de B** |
| P4 | 🟠 ✔ | 204-216 | XP máximo posible = 30 × 30 = **900** → niveles 8 (950), 9, 10 y "Leyenda" (2000) **inalcanzables** |
| P5 | 🟡 | 69-103 | La racha no "decae" al mostrarse: tras 3 días sin jugar sigue mostrando la racha vieja (y el resumen dice "en riesgo" cuando ya se perdió) |
| P6 | 🟡 | 101 | `sesion_hoy` solo se limpia al completar un ejercicio en un día nuevo: el Resumen muestra los de ayer como "de hoy" |
| P7 | 🟡 | 13, 16 | Rutas relativas al directorio actual: correr desde otra carpeta crea/lee otro progreso; `glob` idem |
| P8 | 🟡 | main_window 81 | Nombre de perfil sin sanitizar (`../x` escribe fuera de la carpeta); el perfil elegido no se recuerda al reiniciar |
| P9 | ⚪ | — | Sin versión de esquema (la migración solo agrega campos faltantes) |

### 3.5 UI y otros módulos

| # | Sev | Archivo:línea | Problema |
|---|---|---|---|
| U1 | 🟠 | mapa_window 185-212 | Nivel 8 tiene 9 tarjetas en **una sola fila** (~1370 px) en ventana de 1000 px sin scroll horizontal → tarjetas cortadas |
| U2 | 🟠 | mapa_window 82, 318; resumen 51 | `<MouseWheel>` no existe en Linux (X11 usa `<Button-4/5>`) → sin scroll con rueda; además `bind_all` sobrevive al cerrar la ventana |
| U3 | 🟡 | mapa_window 252-259, 304 | Click en tarjeta: desde el menú principal no hace nada; desde Ejercicios, X2. Si funcionara, saltearía el candado |
| U4 | 🟡 | mapa_window 201-204, 290-294 | Leyenda dice "⭐ Intentado = amarillo" pero 1⭐ se pinta azul igual que 2⭐ |
| U5 | 🟡 | repaso_window 104 y 156 | `__init__` definido **dos veces** (el primero es código muerto); `_init_estado` sin uso; `_personalizar_barra` dice reemplazar botones pero no lo hace |
| U6 | 🟡 | resumen 32, repaso 41, celebracion 26 | `-topmost` en ventanas no modales: el Resumen queda encima de todo, incluso de otras apps |
| U7 | 🟡 | sounds.py | Sonido solo en Windows (`winsound`); en Linux/macOS silencio sin aviso; `except: pass` |
| U8 | 🟡 | error_handler 80-86 | `TimeoutError` (bucle infinito) y `RecursionError` caen en "no es un error común" + detalle técnico **en minúsculas y en inglés** |
| U9 | 🟡 | todas | "Python generado (en vivo)" pero la traducción ocurre al ejecutar (`_traducir_en_vivo` es código muerto en 2 archivos) |
| U10 | ⚪ | celebracion 95-102 | `forma`, `angulo`, `rot` se calculan y no se usan (todo son óvalos) |
| U11 | ⚪ | highlighter 60-61 | Un `#` dentro de un string colorea el resto como comentario |
| U12 | ⚪ | repo | Sin `.gitignore`: 8 `.pyc` versionados (de ahí los "cambios" permanentes en `git status`) |

`utils.centrar_ventana`: correcto, con fallback para Linux/macOS. `ui/__init__.py` existe.

### 3.6 README vs código

| README dice | Código hace |
|---|---|
| `progreso_tortuscript.json` | `progreso_default.json` (y `progreso_<perfil>.json`) |
| "traducción a Python en tiempo real" | solo al ejecutar |
| `preguntar` "en ejercicios muestra un aviso" | abre un diálogo (y dos en la evaluación, X3) |
| "no permite acceso al sistema de archivos" | evadible (E2) |
| "No se puede avanzar sin completar el anterior" | cualquier salida desbloquea (X1) |
| 10 niveles de XP | máximo real: nivel 7 (P4) |
| Estructura sin `tortuga_window`, `highlighter`, `sounds`; sin perfiles ni depurador | existen |
| tabla de lenguaje sin `para`, `hereda de`, tortuga | el traductor los soporta (parcialmente, T7) |

## 4. Seguridad del entorno de ejecución

| Pregunta | Respuesta real |
|---|---|
| ¿`exec` restringido? | Solo superficialmente: builtins recortados, pero `type` y los atributos `__dunder__` abren todo (E2) |
| ¿`import`? | `import os` falla (no hay `__import__`), pero E2 lo esquiva |
| ¿`open/eval/exec/compile/globals`? | No están en builtins; alcanzables vía E2 |
| ¿Límite de iteraciones? | Sí, 50.000 líneas por frame (funciona, E4) |
| ¿Tiempo / memoria / salida? | No (E3) |
| `while True` | Cortado ✔ con mensaje amigable en "Detalle" pero "Explicación" genérica (U8) |
| Recursión infinita | `RecursionError` ✔ capturado, explicación genérica |
| ¿Progreso manipulable? | Es JSON plano: editable a mano (aceptable para uso familiar); corruptible (P1-P3) |

**Riesgo real:** es una app para chicos, no un servidor; el peligro concreto es que un
"copiar/pegar" de internet borre archivos o cuelgue la máquina, no un atacante.

**Sandbox propuesto (sin dependencias):**
1. Validación **AST** antes de ejecutar: rechazar `Import`, `ImportFrom`, cualquier atributo o
   nombre que empiece con `_`, `global`/`nonlocal`; mensaje amigable.
2. Quitar `type` de los builtins (no hace falta para el curso).
3. Contador de pasos **global** (no por frame) y tope de salida (p. ej. 10.000 caracteres).
4. Opcional, más robusto: ejecutar en un **subproceso** (`multiprocessing`) con timeout real y,
   en Linux/macOS, `resource.setrlimit` para memoria; en Windows, solo timeout.

## 5. Pedagogía y UX (10-14 años)

**Lo que ya está bien:** TortuScript al lado de Python real (puente, no muleta), zona libre,
tortuga, repaso con 4 modos, referencia con ejemplos pareados, evaluación por salida.

**Problemas:**
- **Curva:** 8 niveles × 3 ejercicios casi idénticos; nivel 8 "Desafíos" trivial (X7); faltan
  `mientras`, `devolver`, lógica y **ninguna** actividad guiada de tortuga (lo más motivador).
- **Feedback:** mensajes técnicos en inglés ("invalid syntax (<string>, line 1)") delante del
  chico; el `SyntaxError` no dice **qué línea mirar** en lenguaje simple; tildes/mayúsculas (T6)
  generan errores incomprensibles cuando bastaría con aceptarlas.
- **Motivación:** premiar una salida incorrecta (X1) quita sentido a las estrellas; "tu racha
  está en riesgo" es presión estilo Duolingo, discutible a esta edad; niveles inalcanzables (P4)
  frustran al que completa todo.
- **Pistas:** la pista 1 sugiere palabras falsas (X5); la 3 da la solución entera sin paso
  intermedio (mejor: "worked example" parcial o problema de Parsons).
- **Evaluación rígida:** comparación exacta rechaza soluciones creativas válidas (X6).
- **Accesibilidad:** fuente `Consolas` inexistente en Linux, sin zoom de fuente, sin atajos de
  teclado (Ctrl+Enter para ejecutar), textos grises de bajo contraste (#64748b sobre #0f172a).

## 6. Optimización técnica

- Separar **lógica de evaluación** (hoy dentro de `VentanaEjercicios`) a un módulo puro
  testeable (`evaluacion.py`: estrellas, XP, desbloqueo).
- Traductor por **tokens** (`tokenize` de la stdlib) en vez de regex por línea: resuelve T1, T2,
  T4, T9, T10 de raíz y permite `sino si`, `para … en`, tildes y mayúsculas.
- Progreso: escritura atómica (`tmp` + `os.replace`), backup `.bak`, `version` en el JSON, ruta
  absoluta junto al script, perfil pasado explícitamente (no global).
- Unificar las constantes de color duplicadas en 8 archivos.
- Logging a archivo (`logs/`) en lugar de `except: pass`, sin mostrarle nada al chico.
- **No hay tests**: proponer `unittest` (stdlib) para traductor, ejecutor, progreso y
  error_handler.

## 7. Plan de acción priorizado

| Prioridad | Qué | Esfuerzo |
|---|---|---|
| 🔴 Crítico | X2 import de VentanaMapa · X1 salida incorrecta no completa · E1 depurador · T1/T2 variables y/o/no/color · P1/P2 guardado seguro | chico, 1 sesión |
| 🟠 Alto | E2/E3 sandbox AST + tope de salida · T3 tabs · T4 `es` en condiciones · X3 ejercicios con `preguntar` · X4 Limpiar · X5 pistas · P3 perfil · P4 niveles alcanzables · U1 mapa nivel 8 · U2 scroll Linux | medio |
| 🟡 Medio | T5-T8 · X6 consignas · P5/P6 racha y sesión · U3-U9 · README al día · `.gitignore` · tests | medio |
| ⚪ Bajo | T10 · U10-U12 · limpieza de código muerto | chico |

## 8. Roadmap pedagógico (inspirado en otros sistemas)

1. **Tortuga como hilo conductor** (Scratch, Code.org): 1-2 desafíos de dibujo por nivel
   ("dibujá un cuadrado", "una escalera"), evaluados por posición final de la tortuga.
2. **Predecir la salida** antes de ejecutar (Khan Academy, Brilliant): el chico elige qué va a
   mostrar el programa; después lo corre.
3. **Problemas de Parsons** como pista intermedia: las líneas de la solución desordenadas.
4. **Depurar código roto** (retrieval + debugging): ejercicios que empiezan con un bug a arreglar.
5. **Mastery learning** (Khan): avanzar de nivel con 2/3 ejercicios con ≥2⭐, no solo en orden.
6. **Repaso espaciado** (Duolingo, Anki): el modo repaso prioriza lo que no se tocó hace días.
7. **Proyectos libres guiados** (Micro:bit, Tynker): "hacé una calculadora", "un adivinador".
8. **Racha amable**: "días que programaste este mes" en vez de "racha en riesgo".
9. **Modo docente/familia**: exportar/importar progreso, reinicio con confirmación.
10. **Accesibilidad**: tamaño de letra ajustable, alto contraste, Ctrl+Enter, fuente con
    fallback (DejaVu Sans Mono en Linux).

## 9. Entregables pendientes de tu OK

- **Parches** (commits chicos, uno por bug, en una rama `fix/auditoria-20260924`): todo lo 🔴 y
  🟠 de la sección 7.
- **Tests nuevos** (`tests/`, `unittest`, sin dependencias): traductor (todos los casos de 3.1),
  ejecutor (depurador recibe líneas, sandbox bloquea E2, tope de salida, bucle infinito),
  progreso (JSON corrupto no se pierde, escritura atómica, racha, niveles), error_handler
  (TimeoutError/RecursionError amigables).
- **Decisión que necesito de vos antes de tocar el traductor**: ¿arreglo puntual con regex
  (rápido, riesgo bajo) o reescritura por tokens (robusta, cambio más grande)?

## 10. Checklist de verificación manual (después de los parches)

- [ ] `python main.py` abre el menú (Linux y Windows).
- [ ] Ejercicios → 🗺️ Mapa abre y un click en una tarjeta navega al ejercicio.
- [ ] Ejercicio 1 con `mostrar "otra cosa"` → mensaje "no coincide" y **no** deja avanzar.
- [ ] `x es 1` / `y es 2` / `mostrar x + y` → muestra 3.
- [ ] `color es "rojo"` + `mostrar color` → muestra `rojo`.
- [ ] Bloque indentado con Tab → funciona.
- [ ] Zona Tortuga con "Paso a paso" → cada línea se resalta mientras dibuja.
- [ ] `while True: pass` → mensaje amigable de bucle infinito.
- [ ] El código de escape de E2 → bloqueado con mensaje amigable.
- [ ] Ver solución (pista 3) → Limpiar → pegar → sigue dando 1⭐.
- [ ] Ejercicio 7 (`preguntar`) → un solo diálogo y se evalúa bien.
- [ ] Corromper a mano el JSON de progreso → la app avisa y conserva un `.bak`.
- [ ] Cambiar de perfil con Ejercicios abierto → no mezcla progresos.
- [ ] Mapa: el nivel 8 se ve completo; la rueda del mouse scrollea en Linux.
- [ ] Completar los 30 ejercicios con 3⭐ → se alcanza el nivel máximo.
- [ ] `python -m unittest discover tests` → todo verde.
