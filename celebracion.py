import tkinter as tk
import random
import math


class VentanaCelebracion(tk.Toplevel):
    """Ventana emergente de celebración con animación de confetti."""

    COLORES = ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#FF6FC8", "#A855F7"]
    MENSAJES = [
        "🎉 ¡Genial! ¡Lo lograste!",
        "🚀 ¡Sos un crack!",
        "⭐ ¡Perfecto! ¡Sigan así!",
        "🏆 ¡Increíble trabajo!",
        "🔥 ¡Estás en llamas!",
        "💎 ¡Brillante!",
    ]

    def __init__(self, parent, estrellas=3, xp_ganado=0):
        super().__init__(parent)

        self.overrideredirect(True)  # sin borde del sistema
        self.attributes("-topmost", True)
        self.configure(bg="#1a1a2e")

        # Centrar en pantalla
        ancho, alto = 420, 320
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.canvas = tk.Canvas(self, width=ancho, height=alto,
                                 bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.particulas = []
        self._crear_particulas(ancho, alto)

        # Mensaje principal
        self.canvas.create_text(
            ancho // 2, 80,
            text=random.choice(self.MENSAJES),
            font=("Arial", 22, "bold"),
            fill="#FFD93D"
        )

        # Estrellas
        estrellas_txt = "⭐" * estrellas + "☆" * (3 - estrellas)
        self.canvas.create_text(
            ancho // 2, 140,
            text=estrellas_txt,
            font=("Arial", 32),
            fill="#FFD93D"
        )

        # XP
        self.canvas.create_text(
            ancho // 2, 200,
            text=f"+{xp_ganado} XP",
            font=("Arial", 28, "bold"),
            fill="#6BCB77"
        )

        # Botón cerrar
        btn = tk.Button(
            self.canvas,
            text="¡Siguiente! ➡",
            font=("Arial", 13, "bold"),
            bg="#4D96FF",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.destroy,
            cursor="hand2"
        )
        self.canvas.create_window(ancho // 2, 265, window=btn)

        self._animar()

        # Auto-cerrar tras 5 segundos
        self.after(5000, self.destroy)

    def _crear_particulas(self, ancho, alto):
        for _ in range(60):
            x = random.randint(0, ancho)
            y = random.randint(-alto, 0)
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(2, 5)
            size = random.randint(6, 14)
            color = random.choice(self.COLORES)
            forma = random.choice(["rect", "oval"])
            item = self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
            self.particulas.append({
                "item": item, "x": x, "y": y,
                "vx": vx, "vy": vy, "size": size,
                "color": color, "forma": forma,
                "angulo": random.uniform(0, 360),
                "rot": random.uniform(-5, 5)
            })

    def _animar(self):
        if not self.winfo_exists():
            return
        ancho = 420
        alto = 320
        for p in self.particulas:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["angulo"] += p["rot"]
            if p["y"] > alto:
                p["y"] = random.randint(-50, -10)
                p["x"] = random.randint(0, ancho)
            self.canvas.coords(
                p["item"],
                p["x"], p["y"],
                p["x"] + p["size"], p["y"] + p["size"]
            )
        self.after(30, self._animar)
