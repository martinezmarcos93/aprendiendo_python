import tkinter as tk
from tkinter import simpledialog
from ui.ejercicios_window import VentanaEjercicios
from ui.experimentacion_window import ZonaExperimentacion
from ui.mapa_window import VentanaMapa
from ui.repaso_window import SelectorRepaso
from ui.referencia_window import VentanaReferencia
from utils import centrar_ventana
import progreso

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
        frame_perfil = tk.Frame(self, bg=BG)
        frame_perfil.pack(fill="x", pady=(10, 0), padx=20)
        
        self.lbl_perfil = tk.Label(
            frame_perfil, text=f"👤 Perfil: {progreso.PERFIL_ACTUAL}",
            font=("Arial", 11, "bold"), bg=BG, fg="#94a3b8"
        )
        self.lbl_perfil.pack(side=tk.LEFT)
        
        tk.Button(
            frame_perfil, text="Cambiar", font=("Arial", 9), bg="#334155", fg="white",
            relief=tk.FLAT, cursor="hand2", padx=8, command=self._cambiar_perfil
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(self, text="🐢", font=("Arial", 52), bg=BG).pack(pady=(16, 0))

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

    def _cambiar_perfil(self):
        perfiles = progreso.obtener_perfiles()
        msg = "Perfiles existentes:\n" + "\n".join([f"- {p}" for p in perfiles]) + "\n\nIngresá tu nombre de perfil:"
        nuevo = simpledialog.askstring("Cambiar Perfil", msg, parent=self)
        if nuevo:
            nuevo = nuevo.strip().lower()
            if nuevo:
                progreso.set_perfil(nuevo)
                self.lbl_perfil.config(text=f"👤 Perfil: {nuevo}")

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
