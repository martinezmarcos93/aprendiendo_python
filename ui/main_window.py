import tkinter as tk
from ui.ejercicios_window import VentanaEjercicios
from ui.experimentacion_window import ZonaExperimentacion
from ui.mapa_window import VentanaMapa
from ui.repaso_window import SelectorRepaso
from ui.referencia_window import VentanaReferencia
from utils import centrar_ventana

BG = "#0f172a"


class SistemaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐢 TortuScript → Python")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._construir_ui()
        centrar_ventana(self, 520, 620)

    def _construir_ui(self):
        tk.Label(self, text="🐢", font=("Arial", 52), bg=BG).pack(pady=(36, 0))

        tk.Label(
            self, text="TortuScript",
            font=("Arial", 26, "bold"), bg=BG, fg="#f1f5f9"
        ).pack()

        tk.Label(
            self, text="Aprendé Python de a poco, en español",
            font=("Arial", 11), bg=BG, fg="#64748b"
        ).pack(pady=(4, 28))

        botones = [
            ("📚  Ejercicios",             "#f97316", self.abrir_ejercicios),
            ("🧪  Experimentar",           "#22c55e", self.abrir_experimentos),
            ("🗺️   Mapa de Progreso",       "#7c3aed", self.abrir_mapa),
            ("🔁  Repaso",                 "#c2410c", self.abrir_repaso),
            ("📖  Referencia TortuScript", "#0e7490", self.abrir_referencia),
        ]

        frame = tk.Frame(self, bg=BG)
        frame.pack(pady=4)

        for texto, color, cmd in botones:
            tk.Button(
                frame, text=texto,
                font=("Arial", 13, "bold"),
                bg=color, fg="white",
                width=26, height=2,
                relief=tk.FLAT, cursor="hand2",
                command=cmd
            ).pack(pady=6)

        tk.Label(
            self, text="Hecho con 🐢 y mucho amor",
            font=("Arial", 9, "italic"), bg=BG, fg="#334155"
        ).pack(side=tk.BOTTOM, pady=16)

    def abrir_ejercicios(self):
        VentanaEjercicios(self)

    def abrir_experimentos(self):
        ZonaExperimentacion(self)

    def abrir_mapa(self):
        VentanaMapa(self)

    def abrir_repaso(self):
        SelectorRepaso(self)

    def abrir_referencia(self):
        VentanaReferencia(self)
