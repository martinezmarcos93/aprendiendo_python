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
├── main.py                       ← Punto de entrada
├── translator.py                 ← Traduce TortuScript → Python
├── executor.py                   ← Ejecuta el código de forma segura
├── error_handler.py              ← Explica los errores en lenguaje simple
├── ejercicios.py                 ← Los 30 ejercicios del curso
├── progreso.py                   ← Guarda XP, nivel, racha y sesión
├── celebracion.py                ← Animación de confetti al completar
├── utils.py                      ← Utilidades compartidas (centrado de ventanas)
├── progreso_tortuscript.json     ← Guardado automático (se crea solo al jugar)
│
└── ui/
    ├── __init__.py               ← Necesario para que Python reconozca la carpeta
    ├── main_window.py            ← Menú principal
    ├── ejercicios_window.py      ← Ventana principal de ejercicios
    ├── experimentacion_window.py ← Zona libre para experimentar
    ├── mapa_window.py            ← Mapa visual de progreso
    ├── resumen_window.py         ← Resumen de sesión y racha
    ├── repaso_window.py          ← Modo repaso de ejercicios completados
    └── referencia_window.py      ← Guía completa del lenguaje TortuScript
```

---

## Instalación

**Requisitos:** Python 3.8 o superior. tkinter viene incluido con Python en Windows y macOS.

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
30 desafíos organizados en 8 niveles de dificultad progresiva. Cada ejercicio tiene un editor de TortuScript a la izquierda y la traducción a Python en tiempo real a la derecha. Al ejecutar, el programa compara la **salida del programa** con la solución esperada — no el código fuente, así que hay múltiples formas válidas de resolver cada ejercicio.

No se puede avanzar al siguiente ejercicio sin haber completado el anterior.

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

El sistema de pistas da hasta 3 ayudas por ejercicio: palabras clave, primera línea, y solución completa. Usar pistas reduce las estrellas obtenidas.

### 🧪 Experimentar
Zona libre sin ejercicios ni evaluación. Ideal para probar ideas propias. Tiene botones de ejemplos rápidos para arrancar y la misma traducción en vivo.

### 🗺️ Mapa de Progreso
Vista de todos los ejercicios como tarjetas, agrupados por nivel. Muestra el estado de cada uno: verde con borde si tiene 3 estrellas, azul si completó con menos, gris con candado si no lo intentó. Al hacer click en una tarjeta navega directo a ese ejercicio.

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

Completar un ejercicio otorga entre 5 y 30 XP según las estrellas obtenidas. El XP se acumula y sube de nivel al llegar a ciertos umbrales.

| Nivel | Título | XP necesario |
|-------|--------|-------------|
| 1 | 🐣 Aprendiz | 0 |
| 2 | 🐢 Tortuga | 50 |
| 3 | 🐍 Serpiente | 120 |
| 4 | 🦎 Lagarto | 220 |
| 5 | 🦅 Águila | 350 |
| 6 | 🔥 Dragón | 500 |
| 7 | 💎 Cristal | 700 |
| 8 | 🚀 Cohete | 950 |
| 9 | ⚡ Rayo | 1250 |
| 10 | 🏆 Maestro | 1600 |

La racha diaria se incrementa cada día que se completa al menos un ejercicio. Si se saltea un día, la racha se reinicia.

---

## Referencia del lenguaje TortuScript

| TortuScript | Python | Descripción |
|-------------|--------|-------------|
| `mostrar X` | `print(X)` | Mostrar en pantalla |
| `X es Y` | `X = Y` | Asignar variable |
| `preguntar("msg")` | `input("msg")` | Pedir dato al usuario* |
| `si condicion:` | `if condicion:` | Condicional |
| `sino:` | `else:` | Rama alternativa |
| `repetir N veces:` | `for _ in range(N):` | Bucle N veces |
| `mientras condicion:` | `while condicion:` | Bucle mientras |
| `funcion nombre(p):` | `def nombre(p):` | Definir función |
| `devolver X` | `return X` | Retornar valor |
| `clase Nombre:` | `class Nombre:` | Definir clase |
| `y` / `o` / `no` | `and` / `or` / `not` | Operadores lógicos |
| `Verdadero` / `Falso` | `True` / `False` | Booleanos |

> \* `preguntar()` funciona en la zona de Experimentar. En ejercicios muestra un aviso porque no hay terminal disponible.

---

## Dónde se guarda el progreso

El progreso se guarda automáticamente en `progreso_tortuscript.json` en la raíz del proyecto. Para resetear el progreso completamente, borrá ese archivo.

---

## Notas técnicas

- El código del alumno se ejecuta en un entorno restringido (`exec` con builtins limitados) que no permite acceso al sistema de archivos ni importar módulos externos.
- La evaluación compara la **salida del programa** contra la salida esperada de la solución oficial — esto permite que el alumno llegue a la respuesta correcta por distintos caminos.
- La carpeta `ui/` debe contener el archivo `__init__.py` para que Python la reconozca como paquete.
- Probado con Python 3.14 en Windows 11.

---

*Hecho con 🐢 y mucho amor para aprender a programar de a poco.*
