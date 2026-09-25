# 🐢 TortuScript → Python

Un entorno de aprendizaje para que chicos de 10 a 14 años aprendan a programar en Python usando un pseudolenguaje en español llamado **TortuScript**.

---

## ¿Qué es TortuScript?

TortuScript es un lenguaje inventado que se escribe en español y se traduce automáticamente a Python real. La idea es que el chico aprenda la lógica de programar sin que el idioma inglés sea una barrera al principio.

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

## Estructura del proyecto

```
proyecto/
│
├── main.py                       ← Punto de entrada (configura los logs)
├── translator.py                 ← Traduce TortuScript → Python (con tokenize)
├── executor.py                   ← Ejecuta el código del alumno con protecciones
├── error_handler.py              ← Explica los errores en lenguaje simple
├── ejercicios.py                 ← Los 30 ejercicios del curso
├── progreso.py                   ← XP, nivel, racha, sesión y perfiles (guardado seguro)
├── celebracion.py                ← Animación de confetti al completar
├── highlighter.py                ← Resaltado de sintaxis del editor
├── sounds.py                     ← Efectos de sonido (solo Windows)
├── utils.py                      ← Centrado de ventanas y scroll con la rueda
├── progreso_<perfil>.json        ← Guardado automático por perfil (+ copia .bak)
├── config_tortuscript.json       ← Último perfil usado
├── logs/                         ← Errores internos (nunca se muestran al chico)
├── tests/                        ← Tests automáticos (unittest)
├── docs/                         ← Informe de auditoría
│
└── ui/
    ├── __init__.py               ← Necesario para que Python reconozca la carpeta
    ├── main_window.py            ← Menú principal y selector de perfil
    ├── ejercicios_window.py      ← Ventana principal de ejercicios
    ├── experimentacion_window.py ← Zona libre para experimentar
    ├── tortuga_window.py         ← Zona Tortuga (dibujo + depurador paso a paso)
    ├── mapa_window.py            ← Mapa visual de progreso
    ├── resumen_window.py         ← Resumen de sesión y racha
    ├── repaso_window.py          ← Modo repaso de ejercicios completados
    └── referencia_window.py      ← Guía completa del lenguaje TortuScript
```

---

## Instalación

**Requisitos:** Python 3.8 o superior. tkinter viene incluido con Python en Windows y macOS; en Linux (Ubuntu/Debian) instalalo con `sudo apt install python3-tk`.

Para verificar que tenés todo instalado:

```bash
python --version
python -m tkinter
```

Si la segunda línea abre una ventanita, estás listo. No necesita instalar ninguna dependencia externa.

**Para ejecutar:**

```bash
python main.py
```

---

## Modos de la aplicación

### 📚 Ejercicios
30 desafíos organizados en 8 niveles de dificultad progresiva. Cada ejercicio tiene un editor de TortuScript a la izquierda y la traducción a Python en vivo a la derecha (se actualiza mientras escribís). **Ctrl+Enter** ejecuta. Al ejecutar, el programa compara **lo que muestra el programa** con lo que muestra la solución oficial — no el código fuente, así que hay múltiples formas válidas de resolver cada ejercicio. Se toleran espacios al final de las líneas; mayúsculas y tildes cuentan.

Solo una salida correcta completa el ejercicio: si lo que se muestra no coincide, se explica la diferencia y no se avanza. No se puede pasar al siguiente ejercicio sin haber completado el anterior.

| Nivel | Concepto |
|-------|----------|
| 1 | Mostrar texto |
| 2 | Variables |
| 3 | Entrada de datos |
| 4 | Operaciones matemáticas |
| 5 | Condicionales (si / sino) |
| 6 | Bucles (repetir N veces) |
| 7 | Funciones |
| 8 | Desafíos combinados |

El sistema de pistas da hasta 3 ayudas por ejercicio: palabras clave, primera línea, y solución completa. Usar pistas reduce las estrellas obtenidas (3 → 2 → 1). Limpiar el editor no borra las pistas ya vistas.

### 🧪 Experimentar
Zona libre sin ejercicios ni evaluación. Ideal para probar ideas propias. Tiene botones de ejemplos rápidos para arrancar y la misma traducción en vivo.

### 🐢 Zona Tortuga
Dibujo con una tortuga: `avanzar`, `retroceder`, `girar_der`, `girar_izq`, `color`, `subir_lapiz`, `bajar_lapiz`. Con **Paso a paso** activado, cada línea se resalta en el editor mientras la tortuga la ejecuta.

### 🗺️ Mapa de Progreso
Vista de todos los ejercicios como tarjetas, agrupados por nivel. Muestra el estado de cada uno: verde con 3 estrellas, azul con 2, amarillo con 1, gris con candado si todavía no se completó. Al hacer click en una tarjeta se abre ese ejercicio (solo los completados o el siguiente pendiente).

### 📊 Resumen de sesión
Muestra la racha diaria con un mini calendario de los últimos 7 días, los conceptos practicados en la sesión de hoy, y la lista de ejercicios completados con sus estrellas y XP.

### 🔁 Repaso
Permite repasar ejercicios ya completados en cuatro modos:
- **Todo lo completado** — en orden original
- **Solo los imperfectos** — los que no tienen 3 estrellas aún
- **Orden aleatorio** — mezcla todos los completados
- **Los más difíciles** — ordena de menos a más estrellas

### 📖 Referencia TortuScript
Guía completa del lenguaje con todas las construcciones disponibles. Cada concepto muestra el código TortuScript en verde a la izquierda y su equivalente Python en azul a la derecha.

---

## Sistema de XP y niveles

Completar un ejercicio otorga 30 XP (3⭐), 20 XP (2⭐) o 5-10 XP (1⭐, con pistas). El XP solo sube si mejorás tu mejor resultado. Con los 30 ejercicios el máximo es 900 XP, y la escala está pensada para que el nivel 10 se alcance.

| Nivel | Título | XP necesario |
|-------|--------|-------------|
| 1 | 🐣 Aprendiz | 0 |
| 2 | 🐢 Tortuga | 50 |
| 3 | 🐍 Serpiente | 110 |
| 4 | 🦎 Lagarto | 180 |
| 5 | 🦅 Águila | 260 |
| 6 | 🔥 Dragón | 350 |
| 7 | 💎 Cristal | 450 |
| 8 | 🚀 Cohete | 560 |
| 9 | ⚡ Rayo | 680 |
| 10 | 🏆 Maestro | 800 |

La racha diaria se incrementa cada día que se completa al menos un ejercicio. Si se saltea un día, la racha vuelve a cero.

---

## Referencia del lenguaje TortuScript

| TortuScript | Python | Descripción |
|-------------|--------|-------------|
| `mostrar X` | `print(X)` | Mostrar en pantalla |
| `X es Y` | `X = Y` | Asignar variable |
| `si X es Y:` | `if X == Y:` | Dentro de una condición, `es` compara |
| `preguntar("msg")` | `input("msg")` | Pedir dato al usuario |
| `si condicion:` | `if condicion:` | Condicional |
| `sino si condicion:` | `elif condicion:` | Otra condición |
| `sino:` | `else:` | Rama alternativa |
| `repetir N veces:` | `for _ in range(N):` | Bucle N veces (N puede ser una variable) |
| `para x en lista:` | `for x in lista:` | Recorrer una lista |
| `mientras condicion:` | `while condicion:` | Bucle mientras |
| `funcion nombre(p):` | `def nombre(p):` | Definir función |
| `devolver X` | `return X` | Retornar valor |
| `clase Nombre:` | `class Nombre:` | Definir clase |
| `clase Hijo hereda de Padre:` | `class Hijo(Padre):` | Herencia |
| `y` / `o` / `no` | `and` / `or` / `not` | Operadores lógicos |
| `Verdadero` / `Falso` | `True` / `False` | Booleanos |

- Las palabras clave aceptan **tildes y mayúsculas**: `función`, `Mostrar`, `SI`.
- `y`, `o`, `no` y `color` solo se traducen cuando funcionan como operador o comando: se pueden usar como nombres de variables (`y es 3`, `color es "rojo"`).
- La indentación puede ser con espacios o con Tab.
- `preguntar()` abre una ventanita para escribir la respuesta. En los ejercicios, la solución oficial se evalúa con las mismas respuestas que diste.

---

## Dónde se guarda el progreso

El progreso se guarda automáticamente en `progreso_<perfil>.json` junto al programa (el perfil inicial es `default`, así que el archivo es `progreso_default.json`). Cada guardado es atómico y deja una copia `progreso_<perfil>.json.bak` del estado anterior. Si el archivo se daña, se aparta como `.corrupto-<fecha>` y se recupera desde la copia: nunca se pisa en silencio.

Para resetear un perfil, borrá su `progreso_<perfil>.json` (y el `.bak`). Desde **Cambiar** en el menú se puede crear o elegir otro perfil; la app recuerda el último usado.

---

## Notas técnicas

- El código del alumno pasa por una validación previa (no se permite `import` ni nombres que empiecen con `_`) y se ejecuta con builtins limitados, un límite total de 50.000 pasos (corta bucles infinitos) y un tope de 20.000 caracteres de salida. **No es un sandbox para código hostil**: protege al chico de errores y de copiar/pegar cosas peligrosas, pero no limita la memoria.
- Los errores se explican en lenguaje simple, con la línea a mirar; el detalle técnico en inglés aparece aparte, "para curiosos".
- La evaluación compara lo que muestra el programa contra lo que muestra la solución oficial — esto permite llegar a la respuesta correcta por distintos caminos.
- Los sonidos usan `winsound` y solo suenan en Windows.
- Tests: `python -m unittest discover tests` (sin dependencias externas).
- La carpeta `ui/` debe contener el archivo `__init__.py` para que Python la reconozca como paquete.
- Probado con Python 3.12 en Ubuntu 24.04 y Python 3.14 en Windows 11.

---

*Hecho con 🐢 y mucho amor para aprender a programar de a poco.*
