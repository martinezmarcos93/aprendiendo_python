import tkinter as tk
from utils import centrar_ventana
from progreso import (
    cargar_progreso, calcular_nivel, titulo_nivel,
    estrellas_texto, resumen_sesion_hoy
)
from ejercicios import EJERCICIOS

BG_MAIN   = "#0f172a"
BG_CARD   = "#1e293b"
BG_ROW    = "#162032"
VERDE     = "#4ade80"
AMARILLO  = "#fbbf24"
AZUL      = "#60a5fa"
GRIS      = "#94a3b8"
BLANCO    = "#f1f5f9"
MORADO    = "#a78bfa"
ROJO      = "#f87171"
NARANJA   = "#fb923c"


class VentanaResumen(tk.Toplevel):
    """
    Panel de resumen de sesión.
    Se puede llamar en cualquier momento desde ejercicios_window.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 Resumen de hoy")
        centrar_ventana(self, 560, 620)
        self.configure(bg=BG_MAIN)
        self.attributes("-topmost", True)

        self.progreso = cargar_progreso()
        self.resumen  = resumen_sesion_hoy(self.progreso, EJERCICIOS)

        self._construir_ui()

    # ─────────────────────────────────────────
    def _construir_ui(self):
        canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill="y")
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg=BG_MAIN)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        self._seccion_racha(frame)
        self._seccion_nivel(frame)
        self._seccion_conceptos(frame)
        self._seccion_ejercicios(frame)
        self._boton_cerrar(frame)

    # ── Racha
    def _seccion_racha(self, parent):
        racha = self.progreso.get("racha", 0)
        racha_max = self.progreso.get("racha_max", 0)
        ultimo_dia = self.progreso.get("ultimo_dia", "")

        from datetime import date
        es_hoy = ultimo_dia == str(date.today())
        color_racha = NARANJA if racha >= 3 else (AMARILLO if racha >= 1 else GRIS)
        emoji_racha = "🔥" if racha >= 3 else ("⭐" if racha >= 1 else "💤")

        frame = tk.Frame(parent, bg=BG_CARD, pady=16)
        frame.pack(fill="x", padx=20, pady=(20, 8))

        tk.Label(
            frame, text=f"{emoji_racha}  Racha actual",
            font=("Arial", 11), bg=BG_CARD, fg=GRIS
        ).pack()

        tk.Label(
            frame,
            text=f"{racha} día{'s' if racha != 1 else ''}",
            font=("Arial", 36, "bold"), bg=BG_CARD, fg=color_racha
        ).pack()

        tk.Label(
            frame,
            text=f"Mejor racha: {racha_max} días",
            font=("Arial", 10), bg=BG_CARD, fg=GRIS
        ).pack(pady=(2, 0))

        if not es_hoy:
            tk.Label(
                frame,
                text="⚠️  No jugaste hoy todavía — ¡tu racha está en riesgo!",
                font=("Arial", 10), bg=BG_CARD, fg=ROJO
            ).pack(pady=(6, 0))

        # Mini calendario de últimos 7 días
        self._mini_calendario(frame)

    def _mini_calendario(self, parent):
        from datetime import date, timedelta

        dias_activo = set(self.progreso.get("dias_activo", []))
        hoy = date.today()

        frame_cal = tk.Frame(parent, bg=BG_CARD)
        frame_cal.pack(pady=(10, 0))

        tk.Label(
            frame_cal, text="Últimos 7 días:",
            font=("Arial", 9), bg=BG_CARD, fg=GRIS
        ).pack(side=tk.LEFT, padx=(0, 8))

        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            dia_str = str(dia)
            activo = dia_str in dias_activo
            es_hoy_d = (i == 0)

            color_bg = VERDE if activo else GRIS
            color_fg = "#0f2a1a" if activo else BG_CARD
            borde    = AMARILLO if es_hoy_d else color_bg

            c = tk.Canvas(frame_cal, width=28, height=28,
                          bg=BG_CARD, highlightthickness=0)
            c.pack(side=tk.LEFT, padx=2)
            c.create_oval(2, 2, 26, 26, fill=color_bg, outline=borde, width=2)
            c.create_text(14, 14, text=str(dia.day),
                          font=("Arial", 9, "bold"), fill=color_fg)

    # ── Nivel
    def _seccion_nivel(self, parent):
        xp = self.progreso.get("xp_total", 0)
        niv, xp_actual, xp_max = calcular_nivel(xp)

        frame = tk.Frame(parent, bg=BG_CARD, pady=14)
        frame.pack(fill="x", padx=20, pady=8)

        tk.Label(
            frame,
            text=f"{titulo_nivel(niv)}   —   Nivel {niv}",
            font=("Arial", 14, "bold"), bg=BG_CARD, fg=MORADO
        ).pack()

        tk.Label(
            frame, text=f"{xp} XP totales  ({xp_actual}/{xp_max} para el siguiente nivel)",
            font=("Arial", 10), bg=BG_CARD, fg=GRIS
        ).pack(pady=(4, 8))

        # Barra XP
        c = tk.Canvas(frame, width=460, height=14, bg="#334155",
                      highlightthickness=0)
        c.pack()
        if xp_max > 0:
            fill_w = int(460 * xp_actual / xp_max)
            c.create_rectangle(0, 0, fill_w, 14, fill=MORADO, outline="")

    # ── Conceptos aprendidos hoy
    def _seccion_conceptos(self, parent):
        conceptos = self.resumen.get("conceptos", [])
        xp_hoy    = self.resumen.get("xp_ganado_hoy", 0)

        frame = tk.Frame(parent, bg=BG_CARD, pady=14)
        frame.pack(fill="x", padx=20, pady=8)

        tk.Label(
            frame, text="📚  Conceptos practicados hoy",
            font=("Arial", 12, "bold"), bg=BG_CARD, fg=BLANCO
        ).pack(anchor="w", padx=14)

        if not conceptos:
            tk.Label(
                frame,
                text="Todavía no completaste ningún ejercicio hoy.",
                font=("Arial", 11), bg=BG_CARD, fg=GRIS
            ).pack(pady=10)
        else:
            frame_tags = tk.Frame(frame, bg=BG_CARD)
            frame_tags.pack(anchor="w", padx=14, pady=(8, 4))
            for concepto in conceptos:
                tk.Label(
                    frame_tags, text=f"✓ {concepto}",
                    font=("Arial", 11), bg="#0f2a3a", fg=AZUL,
                    padx=10, pady=4
                ).pack(side=tk.LEFT, padx=4)

            tk.Label(
                frame, text=f"+{xp_hoy} XP ganados en esta sesión",
                font=("Arial", 10, "bold"), bg=BG_CARD, fg=VERDE
            ).pack(anchor="w", padx=14, pady=(6, 0))

    # ── Lista de ejercicios completados hoy
    def _seccion_ejercicios(self, parent):
        completados = self.resumen.get("completados", [])
        if not completados:
            return

        frame = tk.Frame(parent, bg=BG_CARD, pady=14)
        frame.pack(fill="x", padx=20, pady=8)

        tk.Label(
            frame, text=f"🏅  Ejercicios de hoy  ({len(completados)})",
            font=("Arial", 12, "bold"), bg=BG_CARD, fg=BLANCO
        ).pack(anchor="w", padx=14, pady=(0, 8))

        for datos in completados:
            fila = tk.Frame(frame, bg=BG_ROW)
            fila.pack(fill="x", padx=10, pady=2)

            tk.Label(
                fila, text=datos["titulo"],
                font=("Arial", 10), bg=BG_ROW, fg=BLANCO,
                anchor="w", width=28
            ).pack(side=tk.LEFT, padx=8, pady=4)

            tk.Label(
                fila, text=estrellas_texto(datos["estrellas"]),
                font=("Arial", 11), bg=BG_ROW, fg=AMARILLO
            ).pack(side=tk.LEFT, padx=4)

            tk.Label(
                fila, text=f"+{datos['xp']} XP",
                font=("Arial", 9), bg=BG_ROW, fg=GRIS
            ).pack(side=tk.RIGHT, padx=10)

    # ── Botón cerrar
    def _boton_cerrar(self, parent):
        tk.Button(
            parent,
            text="¡Listo! ✓",
            font=("Arial", 13, "bold"),
            bg=VERDE, fg="#0f2a1a",
            relief=tk.FLAT, padx=30, pady=10,
            cursor="hand2",
            command=self.destroy
        ).pack(pady=20)
