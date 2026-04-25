import tkinter as tk
from tkinter import scrolledtext
from ejercicios import EJERCICIOS
from translator import TraductorTortuScript
from executor import ejecutar_codigo
from progreso import (
    cargar_progreso, registrar_ejercicio,
    calcular_nivel, titulo_nivel, estrellas_texto
)
from celebracion import VentanaCelebracion
from ui.mapa_window import VentanaMapa
from ui.resumen_window import VentanaResumen

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


class VentanaEjercicios(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📚 TortuScript – Ejercicios")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG_MAIN)
        self.traductor  = TraductorTortuScript()
        self.indice     = 0
        self.progreso   = cargar_progreso()
        self.pista_nivel = 0
        self._construir_ui()
        self.cargar()

    def _construir_ui(self):
        # ── Barra superior
        self.barra_top = tk.Frame(self, bg=BG_CARD, pady=8)
        self.barra_top.pack(fill="x")

        self.lbl_nivel = tk.Label(self.barra_top, text="", font=("Consolas", 11, "bold"), bg=BG_CARD, fg=AMARILLO)
        self.lbl_nivel.pack(side=tk.LEFT, padx=16)

        self.lbl_xp = tk.Label(self.barra_top, text="", font=("Consolas", 11), bg=BG_CARD, fg=AZUL)
        self.lbl_xp.pack(side=tk.LEFT, padx=8)

        self.canvas_xp = tk.Canvas(self.barra_top, height=14, width=200, bg="#334155", highlightthickness=0)
        self.canvas_xp.pack(side=tk.LEFT, padx=8, pady=2)

        self.lbl_racha = tk.Label(self.barra_top, text="", font=("Consolas", 11), bg=BG_CARD, fg="#fb923c")
        self.lbl_racha.pack(side=tk.LEFT, padx=12)

        self.lbl_ejercicio_num = tk.Label(self.barra_top, text="", font=("Consolas", 11), bg=BG_CARD, fg=GRIS)
        self.lbl_ejercicio_num.pack(side=tk.RIGHT, padx=16)

        self.lbl_estrellas_hist = tk.Label(self.barra_top, text="", font=("Arial", 13), bg=BG_CARD, fg=AMARILLO)
        self.lbl_estrellas_hist.pack(side=tk.RIGHT, padx=8)

        tk.Button(
            self.barra_top, text="🗺️ Mapa",
            font=("Arial", 10, "bold"), bg="#7C3AED", fg="white",
            relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
            command=self._abrir_mapa
        ).pack(side=tk.RIGHT, padx=8)

        tk.Button(
            self.barra_top, text="📊 Resumen",
            font=("Arial", 10, "bold"), bg="#0e7490", fg="white",
            relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
            command=self._abrir_resumen
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            self.barra_top, text="🔁 Repaso",
            font=("Arial", 10, "bold"), bg="#c2410c", fg="white",
            relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
            command=self._abrir_repaso
        ).pack(side=tk.RIGHT, padx=4)

        # ── Título
        frame_titulo = tk.Frame(self, bg=BG_MAIN)
        frame_titulo.pack(fill="x", padx=16, pady=(10, 4))

        self.lbl_titulo = tk.Label(frame_titulo, text="", font=("Arial", 16, "bold"), bg=BG_MAIN, fg=BLANCO, anchor="w")
        self.lbl_titulo.pack(side=tk.LEFT)

        self.lbl_tag_nivel = tk.Label(frame_titulo, text="", font=("Arial", 10, "bold"), bg=MORADO, fg=BLANCO, padx=8, pady=2)
        self.lbl_tag_nivel.pack(side=tk.LEFT, padx=10)

        self.lbl_desc = tk.Label(self, text="", font=("Arial", 12), bg=BG_CARD, fg=BLANCO, anchor="w", padx=14, pady=10, wraplength=1060, justify="left")
        self.lbl_desc.pack(fill="x", padx=16, pady=(0, 8))

        # ── Panel central lado a lado
        panel = tk.Frame(self, bg=BG_MAIN)
        panel.pack(fill="both", expand=True, padx=16)
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(1, weight=1)

        tk.Label(panel, text="✏️  Tu código TortuScript", font=("Arial", 11, "bold"), bg=BG_MAIN, fg=VERDE, anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 4))
        tk.Label(panel, text="🐍  Python generado (en vivo)", font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AZUL, anchor="w", padx=10).grid(row=0, column=1, sticky="ew", pady=(0, 4))

        self.editor = scrolledtext.ScrolledText(panel, font=("Consolas", 13), bg=BG_EDITOR, fg=VERDE, insertbackground=VERDE, relief=tk.FLAT, padx=10, pady=10, undo=True)
        self.editor.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.editor.bind("<KeyRelease>", self._traducir_en_vivo)

        self.panel_python = scrolledtext.ScrolledText(panel, font=("Consolas", 13), bg=BG_PYTHON, fg=AZUL, insertbackground=AZUL, relief=tk.FLAT, padx=10, pady=10, state=tk.DISABLED)
        self.panel_python.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        # ── Botones
        barra_btn = tk.Frame(self, bg=BG_MAIN)
        barra_btn.pack(fill="x", padx=16, pady=6)

        tk.Button(barra_btn, text="▶  Ejecutar", font=("Arial", 12, "bold"), bg="#16a34a", fg="white", relief=tk.FLAT, padx=18, pady=6, cursor="hand2", command=self.ejecutar).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_pista = tk.Button(barra_btn, text="💡  Pista (1/3)", font=("Arial", 12, "bold"), bg="#d97706", fg="white", relief=tk.FLAT, padx=18, pady=6, cursor="hand2", command=self.mostrar_pista)
        self.btn_pista.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(barra_btn, text="🗑  Limpiar", font=("Arial", 11), bg="#475569", fg="white", relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self._limpiar).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(barra_btn, text="⬅ Anterior", font=("Arial", 11), bg=BG_CARD, fg=BLANCO, relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.anterior).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(barra_btn, text="Siguiente ➡", font=("Arial", 11), bg=BG_CARD, fg=BLANCO, relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.siguiente).pack(side=tk.RIGHT)

        # ── Salida
        tk.Label(self, text="🖥  Resultado", font=("Arial", 11, "bold"), bg=BG_MAIN, fg=AMARILLO, anchor="w").pack(fill="x", padx=16, pady=(2, 2))

        self.salida = scrolledtext.ScrolledText(self, height=7, font=("Consolas", 11), bg="#0f172a", fg="#e2e8f0", relief=tk.FLAT, padx=10, pady=8)
        self.salida.pack(fill="x", padx=16, pady=(0, 10))
        self.salida.tag_config("ok",    foreground=VERDE)
        self.salida.tag_config("error", foreground=ROJO)
        self.salida.tag_config("info",  foreground=AZUL)
        self.salida.tag_config("pista", foreground=AMARILLO)
        self.salida.tag_config("bold",  font=("Consolas", 11, "bold"))

    def cargar(self):
        ej = EJERCICIOS[self.indice]
        self.pista_nivel = 0
        self.lbl_titulo.config(text=ej["titulo"])
        self.lbl_desc.config(text=f"📋  {ej['descripcion']}")
        self.lbl_tag_nivel.config(text=f"Nivel {ej['nivel']}")
        self.lbl_ejercicio_num.config(text=f"Ejercicio {self.indice + 1} / {len(EJERCICIOS)}")
        hist = self.progreso["ejercicios"].get(str(self.indice), {})
        self.lbl_estrellas_hist.config(text=estrellas_texto(hist.get("estrellas", 0)))
        self.editor.delete("1.0", tk.END)
        self._set_python("")
        self.salida.delete("1.0", tk.END)
        self.btn_pista.config(text="💡  Pista (1/3)", state=tk.NORMAL)
        self._actualizar_barra_xp()

    def _traducir_en_vivo(self, event=None):
        codigo = self.editor.get("1.0", tk.END)
        self._set_python(self.traductor.traducir_codigo(codigo))

    def _set_python(self, texto):
        self.panel_python.config(state=tk.NORMAL)
        self.panel_python.delete("1.0", tk.END)
        self.panel_python.insert("1.0", texto)
        self.panel_python.config(state=tk.DISABLED)

    def ejecutar(self):
        codigo_tortu = self.editor.get("1.0", tk.END).strip()
        if not codigo_tortu:
            self._mostrar_salida([("⚠️  Escribí algo primero.\n", "pista")])
            return
        python = self.traductor.traducir_codigo(codigo_tortu)
        salida_txt, hay_error, msg_error = ejecutar_codigo(python)
        self.salida.delete("1.0", tk.END)
        if hay_error:
            self._mostrar_salida([("❌ Ocurrió un error:\n\n", "error"), (msg_error + "\n", "error")])
            return
        if salida_txt:
            self._mostrar_salida([("✅ Salida:\n", "ok"), (salida_txt + "\n", "bold")])
        else:
            self._mostrar_salida([("✅ Ejecutado sin errores (sin salida).\n", "ok")])
        self._evaluar(codigo_tortu, salida_txt)

    def _evaluar(self, codigo_tortu, salida_txt):
        ej  = EJERCICIOS[self.indice]
        sol = ej.get("solucion", "").strip()

        # Ejecutar la solución oficial para obtener la salida esperada
        python_sol = self.traductor.traducir_codigo(sol)
        salida_esperada, _, _ = ejecutar_codigo(python_sol)

        salida_alumno   = salida_txt.strip()
        salida_correcta = salida_esperada.strip()

        if not salida_alumno:
            # El código no produjo ninguna salida
            self._mostrar_salida([
                ("\n⚠️  Tu código no produjo ninguna salida.\n", "pista"),
                ("   Recordá usar  mostrar  para ver el resultado.\n", "info"),
            ])
            return

        if salida_alumno == salida_correcta:
            # Salida correcta — estrellas según uso de pistas
            if self.pista_nivel == 0:
                estrellas, xp = 3, 30
            elif self.pista_nivel == 1:
                estrellas, xp = 3, 25
            elif self.pista_nivel == 2:
                estrellas, xp = 2, 15
            else:
                estrellas, xp = 1, 8
        else:
            # Hay salida pero no coincide
            estrellas, xp = 1, 5
            self._mostrar_salida([
                ("\n⚠️  Casi! Tu salida no coincide exactamente.\n", "pista"),
                (f"   Esperado:  {salida_correcta}\n", "info"),
                (f"   Tu salida: {salida_alumno}\n", "info"),
            ])
            hubo_mejora = registrar_ejercicio(self.progreso, self.indice, estrellas, xp)
            self.progreso = cargar_progreso()
            self.lbl_estrellas_hist.config(text=estrellas_texto(estrellas))
            self._actualizar_barra_xp()
            if not hubo_mejora:
                self.salida.insert(tk.END, "\n✔ Ya tenías esta estrella guardada.\n", "info")
            return

        hubo_mejora = registrar_ejercicio(self.progreso, self.indice, estrellas, xp)
        self.progreso = cargar_progreso()
        self.lbl_estrellas_hist.config(text=estrellas_texto(estrellas))
        self._actualizar_barra_xp()

        if hubo_mejora:
            self.salida.insert(tk.END, f"\n{estrellas_texto(estrellas)}  +{xp} XP\n", "pista")
            VentanaCelebracion(self, estrellas=estrellas, xp_ganado=xp)
        else:
            self.salida.insert(tk.END, "\n✔ Ya tenías esta estrella guardada.\n", "info")

    def mostrar_pista(self):
        ej     = EJERCICIOS[self.indice]
        sol    = ej.get("solucion", "")
        lineas = sol.strip().split("\n")
        self.pista_nivel += 1
        self.salida.delete("1.0", tk.END)
        if self.pista_nivel == 1:
            keywords = self._detectar_keywords(sol)
            self._mostrar_salida([
                ("💡 Pista 1 — Palabras clave a usar:\n\n", "pista"),
                (f"   {', '.join(keywords)}\n\n", "bold"),
                ("👉 Intentá escribir el código usando esas palabras.\n", "info"),
            ])
            self.btn_pista.config(text="💡  Más pista (2/3)")
        elif self.pista_nivel == 2:
            primera = lineas[0] if lineas else "..."
            self._mostrar_salida([
                ("💡 Pista 2 — La primera línea es:\n\n", "pista"),
                (f"   {primera}\n\n", "bold"),
                (f"   (hay {len(lineas)} línea{'s' if len(lineas)>1 else ''} en total)\n", "info"),
            ])
            self.btn_pista.config(text="💡  Ver solución (3/3)")
        else:
            python = self.traductor.traducir_codigo(sol)
            self._mostrar_salida([
                ("💡 Solución completa:\n\n", "pista"),
                (sol + "\n\n", "bold"),
                ("🐍 En Python sería:\n\n", "info"),
                (python + "\n", "info"),
            ])
            self.btn_pista.config(text="✅ Solución mostrada", state=tk.DISABLED)

    def _detectar_keywords(self, sol):
        palabras = ["mostrar","preguntar","funcion","si","sino","para","mientras","repetir","devolver","clase","es","y","o","no"]
        encontradas = [p for p in palabras if p in sol]
        return encontradas if encontradas else ["mostrar"]

    def _actualizar_barra_xp(self):
        xp = self.progreso.get("xp_total", 0)
        niv, xp_actual, xp_max = calcular_nivel(xp)
        self.lbl_nivel.config(text=f"{titulo_nivel(niv)}  Nv.{niv}")
        self.lbl_xp.config(text=f"{xp} XP  ({xp_actual}/{xp_max})")
        self.canvas_xp.delete("all")
        self.canvas_xp.create_rectangle(0, 0, 200, 14, fill="#334155", outline="")
        if xp_max > 0:
            fill_w = int(200 * xp_actual / xp_max)
            self.canvas_xp.create_rectangle(0, 0, fill_w, 14, fill=AMARILLO, outline="")
        racha = self.progreso.get("racha", 0)
        emoji = "🔥" if racha >= 3 else "⭐"
        self.lbl_racha.config(text=f"{emoji} {racha} día{'s' if racha != 1 else ''}")

    def _mostrar_salida(self, partes):
        for texto, tag in partes:
            self.salida.insert(tk.END, texto, tag)

    def _limpiar(self):
        self.editor.delete("1.0", tk.END)
        self._set_python("")
        self.salida.delete("1.0", tk.END)
        self.pista_nivel = 0
        self.btn_pista.config(text="💡  Pista (1/3)", state=tk.NORMAL)

    def _abrir_resumen(self):
        VentanaResumen(self)

    def _abrir_repaso(self):
        from ui.repaso_window import SelectorRepaso
        SelectorRepaso(self)

    def _abrir_mapa(self):
        def ir_a_ejercicio(indice):
            self.indice = indice
            self.cargar()
        VentanaMapa(self, callback_ir_ejercicio=ir_a_ejercicio)

    def siguiente(self):
        if self.indice < len(EJERCICIOS) - 1:
            self.indice += 1
            self.cargar()

    def anterior(self):
        if self.indice > 0:
            self.indice -= 1
            self.cargar()
