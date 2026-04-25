import random
import tkinter as tk
from ejercicios import EJERCICIOS
from progreso import cargar_progreso, estrellas_texto

BG_MAIN  = "#0f172a"
BG_CARD  = "#1e293b"
AMARILLO = "#fbbf24"
VERDE    = "#4ade80"
AZUL     = "#60a5fa"
GRIS     = "#94a3b8"
BLANCO   = "#f1f5f9"
MORADO   = "#a78bfa"
NARANJA  = "#fb923c"


# ─────────────────────────────────────────────────────────
# Selector de modo — aparece antes de abrir el repaso
# ─────────────────────────────────────────────────────────

class SelectorRepaso(tk.Toplevel):
    """
    Ventana pequeña que pregunta qué tipo de repaso hacer.
    Al confirmar, abre VentanaRepaso con la selección.
    """
    MODOS = [
        ("🔁  Todo lo completado",   "todos"),
        ("⭐  Solo los imperfectos",  "imperfectos"),
        ("🎲  Orden aleatorio",       "aleatorio"),
        ("📉  Los más difíciles",     "dificiles"),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🔁 Modo Repaso")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self.attributes("-topmost", True)
        self._modo_var = tk.StringVar(value="todos")
        self._construir_ui()

    def _construir_ui(self):
        tk.Label(
            self, text="¿Qué querés repasar?",
            font=("Arial", 15, "bold"), bg=BG_MAIN, fg=BLANCO
        ).pack(pady=(24, 4))

        progreso = cargar_progreso()
        completados = sum(
            1 for v in progreso.get("ejercicios", {}).values()
            if v.get("completado")
        )
        imperfectos = sum(
            1 for v in progreso.get("ejercicios", {}).values()
            if v.get("completado") and v.get("estrellas", 0) < 3
        )

        tk.Label(
            self,
            text=f"{completados} ejercicios completados  ·  {imperfectos} sin 3 estrellas",
            font=("Arial", 10), bg=BG_MAIN, fg=GRIS
        ).pack(pady=(0, 16))

        for texto, valor in self.MODOS:
            rb = tk.Radiobutton(
                self, text=texto,
                variable=self._modo_var, value=valor,
                font=("Arial", 12), bg=BG_MAIN, fg=BLANCO,
                selectcolor=BG_CARD, activebackground=BG_MAIN,
                activeforeground=BLANCO, indicatoron=True,
                pady=6
            )
            rb.pack(anchor="w", padx=40)

        tk.Button(
            self,
            text="▶  Empezar repaso",
            font=("Arial", 13, "bold"),
            bg=NARANJA, fg="white",
            relief=tk.FLAT, padx=24, pady=10,
            cursor="hand2",
            command=self._confirmar
        ).pack(pady=24)

    def _confirmar(self):
        modo = self._modo_var.get()
        self.destroy()
        VentanaRepaso(self.parent, modo=modo)


# ─────────────────────────────────────────────────────────
# Ventana de repaso — hereda toda la UI de VentanaEjercicios
# ─────────────────────────────────────────────────────────

from ui.ejercicios_window import VentanaEjercicios  # import local para evitar circular
class VentanaRepaso(VentanaEjercicios):
    """
    Igual que VentanaEjercicios pero con una cola personalizada
    de ejercicios ya completados, en el orden elegido.
    """

    def __init__(self, parent, modo="todos"):
        self.modo = modo
        self._cola = []          # lista de índices a repasar
        self._pos_cola = 0       # posición actual en la cola
        self._construir_cola()   # antes de llamar super().__init__
        super().__init__(parent)

    def _construir_cola(self):
        progreso = cargar_progreso()
        ejercicios_prog = progreso.get("ejercicios", {})

        if self.modo == "todos":
            cola = [
                i for i, _ in enumerate(EJERCICIOS)
                if ejercicios_prog.get(str(i), {}).get("completado")
            ]

        elif self.modo == "imperfectos":
            cola = [
                i for i, _ in enumerate(EJERCICIOS)
                if ejercicios_prog.get(str(i), {}).get("completado")
                and ejercicios_prog.get(str(i), {}).get("estrellas", 0) < 3
            ]

        elif self.modo == "aleatorio":
            cola = [
                i for i, _ in enumerate(EJERCICIOS)
                if ejercicios_prog.get(str(i), {}).get("completado")
            ]
            random.shuffle(cola)

        elif self.modo == "dificiles":
            # Completados con menos estrellas primero
            completados = [
                (i, ejercicios_prog.get(str(i), {}).get("estrellas", 0))
                for i, _ in enumerate(EJERCICIOS)
                if ejercicios_prog.get(str(i), {}).get("completado")
            ]
            completados.sort(key=lambda x: x[1])
            cola = [i for i, _ in completados]

        else:
            cola = list(range(len(EJERCICIOS)))

        self._cola = cola

    # ── Sobreescribir init de estado para arrancar en el primer elemento de la cola
    def _init_estado(self):
        self.indice = self._cola[0] if self._cola else 0
        self._pos_cola = 0

    # ── Sobreescribir __init__ para personalizar título y estado inicial
    def __init__(self, parent, modo="todos"):
        self.modo = modo
        self._cola = []
        self._pos_cola = 0
        self._construir_cola()

        # Llamar a tk.Toplevel directamente (saltear VentanaEjercicios.__init__)
        tk.Toplevel.__init__(self, parent)

        nombres_modo = {
            "todos":       "Todo lo completado",
            "imperfectos": "Sin 3 estrellas",
            "aleatorio":   "Orden aleatorio",
            "dificiles":   "Los más difíciles",
        }
        self.title(f"🔁 Repaso — {nombres_modo.get(modo, '')}")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG_MAIN)

        from translator import TraductorTortuScript
        self.traductor   = TraductorTortuScript()
        self.progreso    = cargar_progreso()
        self.pista_nivel = 0
        self.indice      = self._cola[0] if self._cola else 0

        self._construir_ui()
        self._personalizar_barra()

        if not self._cola:
            self._sin_ejercicios()
        else:
            self.cargar()

    def _personalizar_barra(self):
        """Reemplaza los botones Anterior/Siguiente por los de repaso."""
        # El label de título de la ventana ya indica el modo.
        # Agregamos un indicador de posición en la cola.
        self.lbl_cola = tk.Label(
            self.barra_top,
            text="", font=("Consolas", 10), bg=BG_CARD, fg=NARANJA
        )
        self.lbl_cola.pack(side=tk.LEFT, padx=12)
        self._actualizar_lbl_cola()

    def _actualizar_lbl_cola(self):
        if hasattr(self, "lbl_cola") and self._cola:
            self.lbl_cola.config(
                text=f"🔁 {self._pos_cola + 1}/{len(self._cola)}"
            )

    # ── Navegación sobre la cola
    def siguiente(self):
        if self._pos_cola < len(self._cola) - 1:
            self._pos_cola += 1
            self.indice = self._cola[self._pos_cola]
            self._actualizar_lbl_cola()
            self.cargar()
        else:
            self._fin_repaso()

    def anterior(self):
        if self._pos_cola > 0:
            self._pos_cola -= 1
            self.indice = self._cola[self._pos_cola]
            self._actualizar_lbl_cola()
            self.cargar()

    def _fin_repaso(self):
        """Muestra mensaje de fin de repaso."""
        self.salida.delete("1.0", tk.END)
        self._mostrar_salida([
            ("🎉 ¡Terminaste el repaso!\n\n", "ok"),
            (f"   Repasaste {len(self._cola)} ejercicio{'s' if len(self._cola) != 1 else ''}.\n", "info"),
            ("   Podés cerrar esta ventana o abrir otro modo de repaso.\n", "info"),
        ])

    def _sin_ejercicios(self):
        self.salida.delete("1.0", tk.END)
        self._mostrar_salida([
            ("⚠️  No hay ejercicios para repasar en este modo.\n\n", "pista"),
            ("   Completá algunos ejercicios primero y volvé.\n", "info"),
        ])
