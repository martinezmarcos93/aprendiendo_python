import tkinter as tk
from ui.ejercicios_window import VentanaEjercicios
from ui.experimentacion_window import ZonaExperimentacion
from ui.mapa_window import VentanaMapa
from ui.repaso_window import SelectorRepaso


class SistemaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("🐍 Aprendé Python jugando")
        self.geometry("600x450")
        self.configure(bg="#e3f2fd")

        # -------------------------
        # TÍTULO
        # -------------------------
        tk.Label(
            self,
            text="🐢 TortuScript → Python",
            font=("Arial", 20, "bold"),
            bg="#e3f2fd",
            fg="#0d47a1"
        ).pack(pady=30)

        # -------------------------
        # DESCRIPCIÓN
        # -------------------------
        descripcion = (
            "Elegí cómo querés aprender:\n\n"
            "📚 Ejercicios → Resolvé desafíos paso a paso\n"
            "🧪 Experimentar → Probá tus propias ideas\n"
            "🗺️  Mapa → Ver tu progreso completo\n"
            "🔁 Repaso → Practicá lo que ya aprendiste"
        )

        tk.Label(
            self,
            text=descripcion,
            font=("Arial", 12),
            bg="#e3f2fd",
            fg="#333",
            justify="left"
        ).pack(pady=10)

        # -------------------------
        # BOTONES
        # -------------------------
        frame = tk.Frame(self, bg="#e3f2fd")
        frame.pack(pady=30)

        tk.Button(
            frame,
            text="📚 Ejercicios",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_ejercicios
        ).pack(pady=10)

        tk.Button(
            frame,
            text="🧪 Experimentar",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_experimentos
        ).pack(pady=10)

        tk.Button(
            frame,
            text="🗺️  Mapa de Progreso",
            font=("Arial", 14, "bold"),
            bg="#7C3AED",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_mapa
        ).pack(pady=10)

        tk.Button(
            frame,
            text="🔁 Repaso",
            font=("Arial", 14, "bold"),
            bg="#c2410c",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_repaso
        ).pack(pady=10)

        # -------------------------
        # PIE
        # -------------------------
        tk.Label(
            self,
            text="Aprendé paso a paso como un programador 🚀",
            font=("Arial", 10, "italic"),
            bg="#e3f2fd",
            fg="#555"
        ).pack(side=tk.BOTTOM, pady=20)

    # -------------------------
    # ABRIR VENTANAS
    # -------------------------
    def abrir_ejercicios(self):
        VentanaEjercicios(self)

    def abrir_experimentos(self):
        ZonaExperimentacion(self)

    def abrir_mapa(self):
        VentanaMapa(self)

    def abrir_repaso(self):
        SelectorRepaso(self)