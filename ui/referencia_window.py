import tkinter as tk
from tkinter import scrolledtext
from utils import centrar_ventana

BG_MAIN  = "#0f172a"
BG_CARD  = "#1e293b"
BG_CODE  = "#0d1117"
VERDE    = "#4ade80"
AMARILLO = "#fbbf24"
AZUL     = "#60a5fa"
GRIS     = "#94a3b8"
BLANCO   = "#f1f5f9"
MORADO   = "#a78bfa"
NARANJA  = "#fb923c"
ROJO     = "#f87171"

# Cada sección: (título, color_título, [(descripción, ejemplo_tortu, ejemplo_python), ...])
SECCIONES = [
    ("📺  Mostrar en pantalla", VERDE, [
        ("Mostrar un texto",
         'mostrar "Hola mundo"',
         'print("Hola mundo")'),
        ("Mostrar el valor de una variable",
         'mostrar edad',
         'print(edad)'),
        ("Mostrar texto y variable juntos",
         'mostrar "Hola " + nombre',
         'print("Hola " + nombre)'),
    ]),

    ("📦  Variables", AZUL, [
        ("Guardar un número",
         'edad es 12',
         'edad = 12'),
        ("Guardar un texto",
         'nombre es "Ana"',
         'nombre = "Ana"'),
        ("Guardar el resultado de una operación",
         'suma es 5 + 3',
         'suma = 5 + 3'),
    ]),

    ("➕  Operaciones matemáticas", AMARILLO, [
        ("Suma, resta, multiplicación, división",
         'mostrar 10 + 3\nmostrar 10 - 3\nmostrar 10 * 3\nmostrar 10 / 3',
         'print(10 + 3)\nprint(10 - 3)\nprint(10 * 3)\nprint(10 / 3)'),
        ("Resto (módulo)",
         'mostrar 10 % 3',
         'print(10 % 3)'),
    ]),

    ("🤔  Condicionales", NARANJA, [
        ("Si una condición es verdadera",
         'si edad > 10:\n    mostrar "Mayor"',
         'if edad > 10:\n    print("Mayor")'),
        ("Si / sino",
         'si n % 2 == 0:\n    mostrar "Par"\nsino:\n    mostrar "Impar"',
         'if n % 2 == 0:\n    print("Par")\nelse:\n    print("Impar")'),
        ("Comparadores disponibles",
         '== (igual)   != (distinto)\n>  (mayor)   <  (menor)\n>= (mayor o igual)   <= (menor o igual)',
         '# Igual en Python'),
    ]),

    ("🔄  Bucles", MORADO, [
        ("Repetir N veces",
         'repetir 5 veces:\n    mostrar "Hola"',
         'for _ in range(5):\n    print("Hola")'),
        ("Mientras una condición sea verdadera",
         'n es 0\nmientras n < 5:\n    mostrar n\n    n es n + 1',
         'n = 0\nwhile n < 5:\n    print(n)\n    n = n + 1'),
    ]),

    ("🔧  Funciones", VERDE, [
        ("Definir una función",
         'funcion saludar(nombre):\n    mostrar "Hola " + nombre',
         'def saludar(nombre):\n    print("Hola " + nombre)'),
        ("Llamar a una función",
         'saludar("Ana")',
         'saludar("Ana")'),
        ("Función que devuelve un valor",
         'funcion doble(n):\n    devolver n * 2\n\nresultado es doble(5)\nmostrar resultado',
         'def doble(n):\n    return n * 2\n\nresultado = doble(5)\nprint(resultado)'),
    ]),

    ("🔀  Lógica", ROJO, [
        ("Y (ambas condiciones verdaderas)",
         'si edad > 10 y edad < 18:\n    mostrar "Adolescente"',
         'if edad > 10 and edad < 18:\n    print("Adolescente")'),
        ("O (al menos una verdadera)",
         'si dia == "sábado" o dia == "domingo":\n    mostrar "Fin de semana"',
         'if dia == "sábado" or dia == "domingo":\n    print("Fin de semana")'),
        ("No (negar)",
         'si no nombre == "":\n    mostrar nombre',
         'if not nombre == "":\n    print(nombre)'),
    ]),

    ("📋  Valores especiales", GRIS, [
        ("Booleanos",
         'activo es Verdadero\nsi activo:\n    mostrar "Sí"',
         'activo = True\nif activo:\n    print("Sí")'),
    ]),
]


class VentanaReferencia(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📖 Referencia TortuScript")
        self.configure(bg=BG_MAIN)
        self._construir_ui()
        centrar_ventana(self, 860, 700)

    def _construir_ui(self):
        # Barra superior
        barra = tk.Frame(self, bg=BG_CARD, pady=12)
        barra.pack(fill="x")
        tk.Label(
            barra, text="📖  Referencia del lenguaje TortuScript",
            font=("Arial", 14, "bold"), bg=BG_CARD, fg=BLANCO
        ).pack(side=tk.LEFT, padx=16)
        tk.Label(
            barra, text="Todo lo que podés escribir en TortuScript",
            font=("Arial", 10), bg=BG_CARD, fg=GRIS
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            barra, text="✕  Cerrar",
            font=("Arial", 10), bg=BG_CARD, fg=GRIS,
            relief=tk.FLAT, cursor="hand2",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=16)

        # Canvas con scroll
        canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill="y")
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg=BG_MAIN)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            canvas.find_all()[0], width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        # Intro rápida
        intro = tk.Frame(frame, bg=BG_CARD, pady=12)
        intro.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(
            intro,
            text="TortuScript se escribe en español y se traduce automáticamente a Python.\n"
                 "Cada ejemplo muestra el código TortuScript (verde) y su equivalente Python (azul).",
            font=("Arial", 11), bg=BG_CARD, fg=GRIS,
            justify="left", padx=14
        ).pack(anchor="w")

        # Secciones
        for titulo, color, ejemplos in SECCIONES:
            self._seccion(frame, titulo, color, ejemplos)

        # Pie
        tk.Label(
            frame, text="⌨️  Recordá: la indentación (espacios) es importante en los bloques si/sino/repetir/funcion",
            font=("Arial", 10, "italic"), bg=BG_MAIN, fg=GRIS
        ).pack(pady=(8, 24))

    def _seccion(self, parent, titulo, color, ejemplos):
        # Encabezado de sección
        frame_titulo = tk.Frame(parent, bg=BG_MAIN)
        frame_titulo.pack(fill="x", padx=20, pady=(18, 6))
        tk.Label(
            frame_titulo, text=titulo,
            font=("Arial", 13, "bold"), bg=BG_MAIN, fg=color
        ).pack(side=tk.LEFT)

        for descripcion, tortu, python in ejemplos:
            self._tarjeta_ejemplo(parent, descripcion, tortu, python)

    def _tarjeta_ejemplo(self, parent, descripcion, tortu, python):
        card = tk.Frame(parent, bg=BG_CARD)
        card.pack(fill="x", padx=20, pady=4)

        # Descripción
        tk.Label(
            card, text=descripcion,
            font=("Arial", 10, "bold"), bg=BG_CARD, fg=BLANCO,
            anchor="w", padx=12, pady=6
        ).pack(fill="x")

        # Dos columnas: TortuScript | Python
        cols = tk.Frame(card, bg=BG_CARD)
        cols.pack(fill="x", padx=8, pady=(0, 10))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        # TortuScript
        frame_t = tk.Frame(cols, bg=BG_CODE)
        frame_t.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        tk.Label(
            frame_t, text="TortuScript",
            font=("Arial", 8, "bold"), bg=BG_CODE, fg=VERDE,
            anchor="w", padx=8, pady=3
        ).pack(fill="x")
        tk.Label(
            frame_t, text=tortu,
            font=("Consolas", 11), bg=BG_CODE, fg=VERDE,
            anchor="w", padx=8, pady=6, justify="left"
        ).pack(fill="x")

        # Python
        frame_p = tk.Frame(cols, bg="#0a1628")
        frame_p.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        tk.Label(
            frame_p, text="Python",
            font=("Arial", 8, "bold"), bg="#0a1628", fg=AZUL,
            anchor="w", padx=8, pady=3
        ).pack(fill="x")
        tk.Label(
            frame_p, text=python,
            font=("Consolas", 11), bg="#0a1628", fg=AZUL,
            anchor="w", padx=8, pady=6, justify="left"
        ).pack(fill="x")
