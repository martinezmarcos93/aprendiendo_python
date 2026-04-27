import tkinter as tk
from tkinter import scrolledtext
from utils import centrar_ventana
from translator import TraductorTortuScript
from executor import ejecutar_codigo

BG_MAIN   = "#0f172a"
BG_CARD   = "#1e293b"
BG_EDITOR = "#0d1117"
BG_PYTHON = "#0a1628"
VERDE     = "#4ade80"
AMARILLO  = "#fbbf24"
AZUL      = "#60a5fa"
ROJO      = "#f87171"
GRIS      = "#94a3b8"
BLANCO    = "#f1f5f9"
MORADO    = "#a78bfa"

EJEMPLOS = [
    ("Hola mundo",        'mostrar "Hola mundo"'),
    ("Variable",          'nombre es "Lua"\nmostrar nombre'),
    ("Suma",              'a es 5\nb es 3\nmostrar a + b'),
    ("Condicional",       'edad es 13\nsi edad > 10:\n    mostrar "Mayor"\nsino:\n    mostrar "Menor"'),
    ("Loop",              'repetir 5 veces:\n    mostrar "Hola"'),
    ("Función",           'funcion saludar(nombre):\n    mostrar "Hola " + nombre\n\nsaludar("Lua")'),
]


class ZonaExperimentacion(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🧪 TortuScript – Experimentar")
        centrar_ventana(self, 1100, 700)
        self.configure(bg=BG_MAIN)
        self.traductor = TraductorTortuScript()
        self._construir_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────
    def _construir_ui(self):
        # ── Barra superior
        barra = tk.Frame(self, bg=BG_CARD, pady=10)
        barra.pack(fill="x")

        tk.Label(
            barra, text="🧪  Zona de Experimentación",
            font=("Arial", 14, "bold"), bg=BG_CARD, fg=MORADO
        ).pack(side=tk.LEFT, padx=16)

        tk.Label(
            barra,
            text="Escribí lo que quieras — sin ejercicios, sin límites",
            font=("Arial", 11), bg=BG_CARD, fg=GRIS
        ).pack(side=tk.LEFT, padx=4)

        # ── Accesos rápidos (ejemplos)
        frame_ej = tk.Frame(self, bg=BG_MAIN)
        frame_ej.pack(fill="x", padx=16, pady=(10, 4))

        tk.Label(
            frame_ej, text="Ejemplos rápidos:",
            font=("Arial", 10), bg=BG_MAIN, fg=GRIS
        ).pack(side=tk.LEFT, padx=(0, 8))

        for nombre, codigo in EJEMPLOS:
            tk.Button(
                frame_ej, text=nombre,
                font=("Arial", 10), bg=BG_CARD, fg=AZUL,
                relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
                command=lambda c=codigo: self._cargar_ejemplo(c)
            ).pack(side=tk.LEFT, padx=3)

        # ── Panel central
        panel = tk.Frame(self, bg=BG_MAIN)
        panel.pack(fill="both", expand=True, padx=16, pady=(6, 0))
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Label(
            panel, text="✏️  Tu código TortuScript",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=VERDE, anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))

        tk.Label(
            panel, text="🐍  Python generado (en vivo)",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AZUL, anchor="w", padx=10
        ).grid(row=0, column=1, sticky="ew", pady=(0, 4))

        self.editor = scrolledtext.ScrolledText(
            panel, font=("Consolas", 13),
            bg=BG_EDITOR, fg=VERDE, insertbackground=VERDE,
            relief=tk.FLAT, padx=10, pady=10, undo=True
        )
        self.editor.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.editor.bind("<KeyRelease>", self._traducir_en_vivo)

        self.panel_python = scrolledtext.ScrolledText(
            panel, font=("Consolas", 13),
            bg=BG_PYTHON, fg=AZUL, insertbackground=AZUL,
            relief=tk.FLAT, padx=10, pady=10, state=tk.DISABLED
        )
        self.panel_python.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        # ── Botones
        barra_btn = tk.Frame(self, bg=BG_MAIN)
        barra_btn.pack(fill="x", padx=16, pady=6)

        tk.Button(
            barra_btn, text="▶  Ejecutar",
            font=("Arial", 12, "bold"), bg="#16a34a", fg="white",
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2",
            command=self.ejecutar
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            barra_btn, text="🗑  Limpiar",
            font=("Arial", 11), bg="#475569", fg="white",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
            command=self._limpiar
        ).pack(side=tk.LEFT)

        # ── Salida
        tk.Label(
            self, text="🖥  Resultado",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AMARILLO, anchor="w"
        ).pack(fill="x", padx=16, pady=(2, 2))

        self.salida = scrolledtext.ScrolledText(
            self, height=8, font=("Consolas", 11),
            bg="#0f172a", fg="#e2e8f0", relief=tk.FLAT, padx=10, pady=8
        )
        self.salida.pack(fill="x", padx=16, pady=(0, 10))
        self.salida.tag_config("ok",    foreground=VERDE)
        self.salida.tag_config("error", foreground=ROJO)
        self.salida.tag_config("info",  foreground=AZUL)
        self.salida.tag_config("bold",  font=("Consolas", 11, "bold"))

    # ─────────────────────────────────────────
    # ACCIONES
    # ─────────────────────────────────────────
    def ejecutar(self):
        codigo = self.editor.get("1.0", tk.END).strip()
        if not codigo:
            self._set_salida([("⚠️  Escribí algo primero.\n", "info")])
            return

        python = self.traductor.traducir_codigo(codigo)
        self._set_python(python)

        salida, hay_error, msg_error = ejecutar_codigo(python)
        self.salida.delete("1.0", tk.END)

        if hay_error:
            self._set_salida([("❌ Ocurrió un error:\n\n", "error"), (msg_error + "\n", "error")])
        elif salida:
            self._set_salida([("✅ Salida:\n", "ok"), (salida, "bold")])
        else:
            self._set_salida([("✅ Ejecutado sin errores (sin salida visible).\n", "ok")])

    def _traducir_en_vivo(self, event=None):
        codigo = self.editor.get("1.0", tk.END)
        self._set_python(self.traductor.traducir_codigo(codigo))

    def _cargar_ejemplo(self, codigo):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", codigo)
        self._set_python(self.traductor.traducir_codigo(codigo))
        self.salida.delete("1.0", tk.END)

    def _limpiar(self):
        self.editor.delete("1.0", tk.END)
        self._set_python("")
        self.salida.delete("1.0", tk.END)

    def _set_python(self, texto):
        self.panel_python.config(state=tk.NORMAL)
        self.panel_python.delete("1.0", tk.END)
        self.panel_python.insert("1.0", texto)
        self.panel_python.config(state=tk.DISABLED)

    def _set_salida(self, partes):
        self.salida.delete("1.0", tk.END)
        for texto, tag in partes:
            self.salida.insert(tk.END, texto, tag)
