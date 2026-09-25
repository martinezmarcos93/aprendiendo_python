import tkinter as tk
from tkinter import font as tkfont
from tortuscript.ejercicios import EJERCICIOS
from utils import centrar_ventana, habilitar_rueda
from tortuscript.progreso import (
    cargar_progreso, calcular_nivel, titulo_nivel, estrellas_texto
)

BG_MAIN    = "#0f172a"
BG_CARD    = "#1e293b"
BG_HOVER   = "#263548"
VERDE      = "#4ade80"
AMARILLO   = "#fbbf24"
AZUL       = "#60a5fa"
GRIS       = "#94a3b8"
GRIS_OSC   = "#334155"
BLANCO     = "#f1f5f9"
MORADO     = "#a78bfa"
ROJO       = "#f87171"

# Color por nivel de concepto
COLOR_NIVEL = {
    1: ("#fbbf24", "#78350f"),   # amarillo
    2: ("#60a5fa", "#1e3a5f"),   # azul
    3: ("#a78bfa", "#3b1f6e"),   # morado
    4: ("#34d399", "#064e3b"),   # verde
    5: ("#f87171", "#7f1d1d"),   # rojo
    6: ("#fb923c", "#7c2d12"),   # naranja
    7: ("#e879f9", "#701a75"),   # rosa
    8: ("#38bdf8", "#0c4a6e"),   # celeste
}

NOMBRE_NIVEL = {
    1: "MOSTRAR",
    2: "VARIABLES",
    3: "INPUT",
    4: "OPERACIONES",
    5: "CONDICIONALES",
    6: "BUCLES",
    7: "FUNCIONES",
    8: "DESAFÍOS",
}


class VentanaMapa(tk.Toplevel):
    def __init__(self, parent, callback_ir_ejercicio=None):
        super().__init__(parent)
        self.title("🗺️  TortuScript – Mapa de Progreso")
        self.configure()
        centrar_ventana(self, 1000, 680)
        self.configure(bg=BG_MAIN)

        # callback para navegar directo a un ejercicio
        self.callback_ir = callback_ir_ejercicio

        self.progreso = cargar_progreso()
        self._construir_ui()

    # ─────────────────────────────────────────
    # UI PRINCIPAL
    # ─────────────────────────────────────────
    def _construir_ui(self):
        # ── Barra superior con stats globales
        self._barra_stats()

        # ── Canvas scrolleable con el mapa
        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(wrapper, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        self.frame_mapa = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_mapa, anchor="nw")

        self.frame_mapa.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        habilitar_rueda(self.canvas)

        self._dibujar_mapa()

    def _barra_stats(self):
        barra = tk.Frame(self, bg=BG_CARD, pady=12)
        barra.pack(fill="x")

        xp = self.progreso.get("xp_total", 0)
        niv, xp_actual, xp_max = calcular_nivel(xp)

        # Título
        tk.Label(
            barra, text="🗺️  Mapa de Progreso",
            font=("Arial", 14, "bold"), bg=BG_CARD, fg=BLANCO
        ).pack(side=tk.LEFT, padx=16)

        # Stats al centro
        completados = sum(
            1 for v in self.progreso.get("ejercicios", {}).values()
            if v.get("completado")
        )
        tres_estrellas = sum(
            1 for v in self.progreso.get("ejercicios", {}).values()
            if v.get("estrellas", 0) == 3
        )
        total = len(EJERCICIOS)

        for texto, valor, color in [
            ("Ejercicios", f"{completados}/{total}", VERDE),
            ("3 estrellas", str(tres_estrellas), AMARILLO),
            ("XP total", str(xp), AZUL),
            (titulo_nivel(niv), f"Nv.{niv}", MORADO),
        ]:
            frame_stat = tk.Frame(barra, bg=BG_CARD)
            frame_stat.pack(side=tk.LEFT, padx=20)
            tk.Label(frame_stat, text=valor, font=("Arial", 16, "bold"),
                     bg=BG_CARD, fg=color).pack()
            tk.Label(frame_stat, text=texto, font=("Arial", 9),
                     bg=BG_CARD, fg=GRIS).pack()

        # Barra XP
        frame_xp = tk.Frame(barra, bg=BG_CARD)
        frame_xp.pack(side=tk.RIGHT, padx=20)
        tk.Label(frame_xp, text=f"{xp_actual}/{xp_max} XP",
                 font=("Arial", 9), bg=BG_CARD, fg=GRIS).pack(anchor="e")
        c = tk.Canvas(frame_xp, width=160, height=10, bg=GRIS_OSC, highlightthickness=0)
        c.pack()
        if xp_max > 0:
            fill_w = int(160 * xp_actual / xp_max)
            c.create_rectangle(0, 0, fill_w, 10, fill=AMARILLO, outline="")

    # ─────────────────────────────────────────
    # MAPA POR NIVELES
    # ─────────────────────────────────────────
    def _dibujar_mapa(self):
        # Agrupar ejercicios por nivel
        niveles = {}
        for i, ej in enumerate(EJERCICIOS):
            nv = ej["nivel"]
            if nv not in niveles:
                niveles[nv] = []
            niveles[nv].append((i, ej))

        for nv in sorted(niveles.keys()):
            self._dibujar_nivel(nv, niveles[nv])

        # Pie con leyenda
        self._dibujar_leyenda()

    def _dibujar_nivel(self, nv, ejercicios):
        color_fg, color_bg = COLOR_NIVEL.get(nv, (BLANCO, BG_CARD))
        nombre = NOMBRE_NIVEL.get(nv, f"NIVEL {nv}")

        # ── Encabezado del nivel
        frame_header = tk.Frame(self.frame_mapa, bg=BG_MAIN)
        frame_header.pack(fill="x", padx=24, pady=(20, 6))

        # Línea decorativa con nombre
        tk.Label(
            frame_header,
            text=f"  NIVEL {nv} — {nombre}  ",
            font=("Consolas", 10, "bold"),
            bg=color_bg, fg=color_fg,
            padx=12, pady=4
        ).pack(side=tk.LEFT)

        # Progreso del nivel
        completados_nv = sum(
            1 for (i, _) in ejercicios
            if self.progreso["ejercicios"].get(str(i), {}).get("completado")
        )
        total_nv = len(ejercicios)
        tk.Label(
            frame_header,
            text=f"{completados_nv}/{total_nv} completados",
            font=("Arial", 10), bg=BG_MAIN, fg=GRIS
        ).pack(side=tk.LEFT, padx=12)

        # ── Grilla de ejercicios
        frame_grilla = tk.Frame(self.frame_mapa, bg=BG_MAIN)
        frame_grilla.pack(fill="x", padx=24, pady=(0, 4))

        for col, (i, ej) in enumerate(ejercicios):
            self._tarjeta_ejercicio(frame_grilla, i, ej, nv, col)

    def _tarjeta_ejercicio(self, parent, indice, ej, nv, col):
        datos = self.progreso["ejercicios"].get(str(indice), {})
        completado = datos.get("completado", False)
        estrellas  = datos.get("estrellas", 0)
        xp_ganado  = datos.get("xp", 0)

        color_fg, color_bg_badge = COLOR_NIVEL.get(nv, (BLANCO, BG_CARD))

        # Estado visual
        if completado and estrellas == 3:
            bg_card  = "#0f2a1a"
            borde    = VERDE
            num_color = VERDE
        elif completado and estrellas == 2:
            bg_card  = "#1a2040"
            borde    = AZUL
            num_color = AZUL
        elif completado:
            bg_card  = "#2a2410"
            borde    = AMARILLO
            num_color = AMARILLO
        else:
            bg_card  = BG_CARD
            borde    = GRIS_OSC
            num_color = GRIS

        # Marco con borde coloreado
        frame_outer = tk.Frame(parent, bg=borde, padx=1, pady=1)
        # 5 tarjetas por fila: el nivel 8 tiene 9 ejercicios y no entraba en una sola
        frame_outer.grid(row=col // 5, column=col % 5, padx=6, pady=4, sticky="n")

        frame_card = tk.Frame(frame_outer, bg=bg_card, width=140, height=110)
        frame_card.pack()
        frame_card.pack_propagate(False)

        # Número del ejercicio
        titulo_corto = ej["titulo"].split(". ", 1)
        numero = titulo_corto[0] if len(titulo_corto) > 1 else str(indice + 1)
        nombre = titulo_corto[1] if len(titulo_corto) > 1 else ej["titulo"]

        tk.Label(
            frame_card, text=f"#{numero}",
            font=("Consolas", 11, "bold"),
            bg=bg_card, fg=num_color
        ).pack(pady=(10, 2))

        tk.Label(
            frame_card, text=nombre,
            font=("Arial", 9), bg=bg_card, fg=BLANCO,
            wraplength=120, justify="center"
        ).pack(padx=6)

        # Estrellas o candado
        if completado:
            stars_txt = "⭐" * estrellas + "☆" * (3 - estrellas)
            tk.Label(
                frame_card, text=stars_txt,
                font=("Arial", 11), bg=bg_card, fg=AMARILLO
            ).pack(pady=(4, 0))
            tk.Label(
                frame_card, text=f"+{xp_ganado} XP",
                font=("Arial", 8), bg=bg_card, fg=GRIS
            ).pack()
        else:
            tk.Label(
                frame_card, text="🔒",
                font=("Arial", 16), bg=bg_card, fg=GRIS
            ).pack(pady=(6, 0))

        # Click para ir al ejercicio (siempre: desde el menú abre la ventana de ejercicios)
        if True:
            for widget in [frame_card, frame_outer]:
                widget.bind("<Button-1>", lambda e, idx=indice: self._ir_a(idx))
                widget.configure(cursor="hand2")
            for child in frame_card.winfo_children():
                child.bind("<Button-1>", lambda e, idx=indice: self._ir_a(idx))
                child.configure(cursor="hand2")

        # Hover
        def on_enter(e, f=frame_card, bg=bg_card):
            f.configure(bg=BG_HOVER)
            for w in f.winfo_children():
                try:
                    w.configure(bg=BG_HOVER)
                except Exception:
                    pass

        def on_leave(e, f=frame_card, bg=bg_card):
            f.configure(bg=bg)
            for w in f.winfo_children():
                try:
                    w.configure(bg=bg)
                except Exception:
                    pass

        frame_card.bind("<Enter>", on_enter)
        frame_card.bind("<Leave>", on_leave)

    def _dibujar_leyenda(self):
        frame = tk.Frame(self.frame_mapa, bg=BG_CARD)
        frame.pack(fill="x", padx=24, pady=(16, 24))

        tk.Label(
            frame, text="Leyenda:",
            font=("Arial", 10, "bold"), bg=BG_CARD, fg=GRIS
        ).pack(side=tk.LEFT, padx=12, pady=8)

        for texto, color in [
            ("⭐⭐⭐ Perfecto", VERDE),
            ("⭐⭐ Completo", AZUL),
            ("⭐ Intentado", AMARILLO),
            ("🔒 Sin completar", GRIS),
        ]:
            tk.Label(
                frame, text=texto,
                font=("Arial", 10), bg=BG_CARD, fg=color
            ).pack(side=tk.LEFT, padx=14, pady=8)

    # ─────────────────────────────────────────
    # NAVEGACIÓN
    # ─────────────────────────────────────────
    def _indice_permitido(self, indice):
        """Se puede ir a un ejercicio ya completado o al primero sin completar."""
        ej = self.progreso.get("ejercicios", {})
        if ej.get(str(indice), {}).get("completado"):
            return True
        primero_pendiente = next(
            (i for i in range(len(EJERCICIOS)) if not ej.get(str(i), {}).get("completado")), None)
        return indice == primero_pendiente

    def _ir_a(self, indice):
        if not self._indice_permitido(indice):
            self.title("🔒 Completá los ejercicios anteriores para desbloquear ese")
            return
        if self.callback_ir:
            self.callback_ir(indice)
        else:
            from ui.ejercicios_window import VentanaEjercicios
            ventana = VentanaEjercicios(self.master)
            ventana.indice = indice
            ventana.cargar()
        self.destroy()

    # ─────────────────────────────────────────
    # SCROLL
    # ─────────────────────────────────────────
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)


