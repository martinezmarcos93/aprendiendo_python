import tkinter as tk
from tkinter import scrolledtext
from utils import centrar_ventana
from translator import TraductorTortuScript, detectar_tipo
from executor import ejecutar_codigo
from highlighter import TortuHighlighter
from sounds import play_sound
import turtle
import time

BG_MAIN   = "#0f172a"
BG_CARD   = "#1e293b"
BG_EDITOR = "#0d1117"
VERDE     = "#4ade80"
AZUL      = "#60a5fa"
ROJO      = "#f87171"
BLANCO    = "#f1f5f9"
MORADO    = "#a78bfa"
GRIS      = "#94a3b8"
AMARILLO  = "#fbbf24"


class ZonaTortuga(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🐢 TortuScript – Zona Tortuga")
        centrar_ventana(self, 1100, 700)
        self.configure(bg=BG_MAIN)
        self.traductor = TraductorTortuScript()
        self._construir_ui()
        self._init_turtle()

    def _construir_ui(self):
        # Barra superior
        barra = tk.Frame(self, bg=BG_CARD, pady=10)
        barra.pack(fill="x")
        
        tk.Label(
            barra, text="🐢  Zona Tortuga",
            font=("Arial", 14, "bold"), bg=BG_CARD, fg=MORADO
        ).pack(side=tk.LEFT, padx=16)

        tk.Label(
            barra, text="Dale órdenes a la tortuga: avanzar, girar_der, girar_izq, color, subir_lapiz, bajar_lapiz",
            font=("Arial", 11), bg=BG_CARD, fg=GRIS
        ).pack(side=tk.LEFT, padx=4)

        # Panel central
        panel = tk.Frame(self, bg=BG_MAIN)
        panel.pack(fill="both", expand=True, padx=16, pady=(10, 0))
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Label(
            panel, text="✏️  Tu código",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=VERDE, anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        
        tk.Label(
            panel, text="🎨  Lienzo",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AZUL, anchor="w", padx=10
        ).grid(row=0, column=1, sticky="ew", pady=(0, 4))

        self.editor = scrolledtext.ScrolledText(
            panel, font=("Consolas", 13),
            bg=BG_EDITOR, fg=BLANCO, insertbackground=BLANCO,
            relief=tk.FLAT, padx=10, pady=10, undo=True
        )
        self.editor.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.hl_editor = TortuHighlighter(self.editor, es_python=False)

        # Turtle Canvas
        frame_canvas = tk.Frame(panel, bg="white", highlightthickness=2, highlightbackground=GRIS)
        frame_canvas.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
        
        self.canvas = tk.Canvas(frame_canvas, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Barra botones
        barra_btn = tk.Frame(self, bg=BG_MAIN)
        barra_btn.pack(fill="x", padx=16, pady=6)
        
        tk.Button(
            barra_btn, text="▶  Dibujar",
            font=("Arial", 12, "bold"), bg="#16a34a", fg="white",
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2",
            command=self.ejecutar
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            barra_btn, text="🗑  Limpiar Todo",
            font=("Arial", 11), bg="#475569", fg="white",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
            command=self._limpiar
        ).pack(side=tk.LEFT)

        self.var_depurador = tk.BooleanVar(value=True)
        tk.Checkbutton(
            barra_btn, text="Paso a paso (Depurador)", variable=self.var_depurador,
            bg=BG_MAIN, fg="white", selectcolor=BG_CARD,
            activebackground=BG_MAIN, activeforeground="white"
        ).pack(side=tk.LEFT, padx=16)

        # Salida
        tk.Label(
            self, text="🖥  Consola",
            font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AMARILLO, anchor="w"
        ).pack(fill="x", padx=16, pady=(2, 2))
        
        self.salida = scrolledtext.ScrolledText(
            self, height=5, font=("Consolas", 11),
            bg="#0f172a", fg="#e2e8f0", relief=tk.FLAT, padx=10, pady=8
        )
        self.salida.pack(fill="x", padx=16, pady=(0, 10))
        self.salida.tag_config("ok", foreground=VERDE)
        self.salida.tag_config("error", foreground=ROJO)
        self.salida.tag_config("info", foreground=AZUL)
        self.salida.tag_config("bold", font=("Consolas", 11, "bold"))

    def _init_turtle(self):
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor("white")
        self.t = turtle.RawTurtle(self.screen)
        self.t.shape("turtle")
        self.t.color("#16a34a")
        self.t.speed(3)

    def _limpiar(self):
        self.editor.delete("1.0", tk.END)
        self.t.clear()
        self.t.penup()
        self.t.home()
        self.t.pendown()
        self.t.color("#16a34a")
        self.salida.delete("1.0", tk.END)

    def ejecutar(self):
        codigo = self.editor.get("1.0", tk.END).strip()
        if not codigo:
            self._set_salida([("⚠️  Escribí algo primero.\n", "info")])
            return

        # Limpiar lienzo antes de ejecutar
        self.t.clear()
        self.t.penup()
        self.t.home()
        self.t.pendown()
        self.t.color("#16a34a")
        
        tipo = detectar_tipo(codigo)
        python = codigo if tipo == "python" else self.traductor.traducir_codigo(codigo)

        # Funciones de tortuga
        def avanzar(dist): self.t.forward(dist)
        def girar_der(angulo): self.t.right(angulo)
        def girar_izq(angulo): self.t.left(angulo)
        def color(c): self.t.color(c)
        def bajar_lapiz(): self.t.pendown()
        def subir_lapiz(): self.t.penup()

        extra_globals = {
            "avanzar": avanzar,
            "girar_der": girar_der,
            "girar_izq": girar_izq,
            "color": color,
            "bajar_lapiz": bajar_lapiz,
            "subir_lapiz": subir_lapiz,
        }

        def _callback_linea(num_linea):
            if not self.var_depurador.get():
                return
            self.editor.tag_remove("current_line", "1.0", tk.END)
            self.editor.tag_add("current_line", f"{num_linea}.0", f"{num_linea}.end")
            self.editor.tag_config("current_line", background="#334155")
            self.editor.update()
            self.canvas.update()
            time.sleep(0.4)

        salida, hay_error, msg_error = ejecutar_codigo(python, extra_globals=extra_globals, callback_linea=_callback_linea)
        
        self.editor.tag_remove("current_line", "1.0", tk.END)
        self.editor.update()
        
        if hay_error:
            play_sound("error")
            self._set_salida([("❌ Ocurrió un error:\n\n", "error"), (msg_error + "\n", "error")])
        else:
            play_sound("success")
            self._set_salida([("✅ Dibujo completado.\n", "ok")])
            if salida:
                self.salida.insert(tk.END, salida + "\n", "bold")

    def _set_salida(self, partes):
        self.salida.delete("1.0", tk.END)
        for texto, tag in partes:
            self.salida.insert(tk.END, texto, tag)
