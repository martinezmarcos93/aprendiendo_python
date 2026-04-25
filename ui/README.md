# 🐢 TortuScript → Python

Un entorno de aprendizaje para que chicos de 10 a 14 años aprendan a programar en Python usando un pseudolenguaje en español llamado **TortuScript**.

---

## ¿Qué es TortuScript?

TortuScript es un lenguaje inventado que se escribe en español y se traduce automáticamente a Python real. La idea es que el chico aprenda la lógica de programar sin que el idioma inglés sea una barrera al principio.

```
# TortuScript          →     Python
mostrar "Hola mundo"   →     print("Hola mundo")
nombre es "Juan"       →     nombre = "Juan"
si edad > 10:          →     if edad > 10:
    mostrar "Grande"   →         print("Grande")
repetir 3 veces:       →     for _ in range(3):
    mostrar "Hola"     →         print("Hola")
funcion saludar(n):    →     def saludar(n):
    mostrar n          →         print(n)
```

---

## Estructura del proyecto

```
tortuscript/
│
├── main.py                      ← Punto de entrada
├── translator.py                ← Traduce TortuScript → Python
├── executor.py                  ← Ejecuta el código de forma segura
├── error_handler.py             ← Explica los errores en lenguaje simple
├── ejercicios.py                ← Los 30 ejercicios del curso
├── progreso.py                  ← Guarda XP, nivel, racha y sesión
├── celebracion.py               ← Animación de confetti al completar
├── progreso_tortuscript.json    ← Guardado automático del progreso
│
└── ui/
    ├── main_window.py           ← Menú principal
    ├── ejercicios_window.py     ← Ventana principal de ejercicios
    ├── experimentacion_window.py← Zona libre para experimentar
    ├── mapa_window.py           ← Mapa visual de progreso
    ├── resumen_window.py        ← Resumen de sesión y racha
    └── repaso_window.py         ← Modo repaso de ejercicios completados
```

---

## Requisitos

- Python 3.8 o superior
- tkinter (viene incluido con Python en Windows y macOS)

Para verificar que tenés todo instalado, abrí una terminal y ejecutá:

```bash
python --version
python -m tkinter
```

Si la segunda línea abre una ventanita, estás listo.

---

## Instalación y uso

```bash
# 1. Clonar o descomprimir el proyecto
cd tortuscript

# 2. Ejecutar
python main.py
```

No necesita instalar ninguna dependencia externa.

---

## Modos de la aplicación

### 📚 Ejercicios
30 desafíos organizados en 8 niveles de dificultad progresiva. Cada ejercicio tiene un editor de TortuScript a la izquierda y la traducción a Python en tiempo real a la derecha. Al ejecutar, el programa compara la salida del código con la solución esperada.

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
Vista de todos los ejercicios como tarjetas, agrupados por nivel. Muestra el estado de cada uno (completado con 3 estrellas, completado, o sin intentar). Al hacer click en una tarjeta navega directo a ese ejercicio.

### 📊 Resumen de sesión
Muestra la racha diaria con un mini calendario de los últimos 7 días, los conceptos practicados en la sesión de hoy, y la lista de ejercicios completados con sus estrellas y XP.

### 🔁 Repaso
Permite repasar ejercicios ya completados en cuatro modos:
- **Todo lo completado** — en orden original
- **Solo los imperfectos** — los que no tienen 3 estrellas aún
- **Orden aleatorio** — mezcla todos los completados
- **Los más difíciles** — ordena de menos a más estrellas

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

El progreso se guarda automáticamente en `progreso_tortuscript.json` en la misma carpeta del proyecto. Para resetear el progreso simplemente borrá ese archivo.

---

## Notas para el que lo instala

- El código se ejecuta en un entorno restringido (`exec` con builtins limitados) que no permite acceso al sistema de archivos ni importar módulos.
- Si en algún momento el chico quiere escribir un programa con `preguntar()`, la zona de Experimentar aún no tiene soporte de entrada interactiva en esta versión. Es una mejora planeada para una versión futura.
- Los archivos `ui/ejercicios_window.py`, `ui/experimentacion_window.py`, `ui/mapa_window.py`, `ui/resumen_window.py` y `ui/repaso_window.py` deben estar dentro de la carpeta `ui/`. Los demás van en la raíz.

---

*Hecho con 🐢 y mucho amor para aprender a programar de a poco.*
