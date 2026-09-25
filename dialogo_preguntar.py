"""
Ventanita de preguntar() con la estética de TortuScript.

- Se abre centrada ENCIMA de la ventana desde la que se ejecutó el código
  (Ejercicios, Experimentar o Tortuga), sin traer al frente el menú principal.
- Enter y el Intro del teclado numérico confirman; Escape cancela.
"""
import logging
import tkinter as tk

logger = logging.getLogger("tortuscript.dialogo")

# Enter normal y el del teclado numérico, por nombre, por código físico (X11/Windows)
# y por el carácter que producen: así funciona con cualquier mapa de teclado.
_TECLAS_ENTER = {"Return", "KP_Enter"}
_CODIGOS_ENTER = {36, 104, 13}

BG_MAIN   = "#0f172a"
BG_CARD   = "#1e293b"
BG_EDITOR = "#0d1117"
BLANCO    = "#f1f5f9"
GRIS      = "#94a3b8"
VERDE_BTN = "#16a34a"
BORDE     = "#7c3aed"


class DialogoPreguntar(tk.Toplevel):
    def __init__(self, padre, pregunta):
        super().__init__(padre)
        self.respuesta = None
        self.withdraw()                      # armar oculto y mostrar ya ubicado
        self.title("✏️  Tu programa pregunta")
        self.configure(bg=BORDE)             # marco violeta de 2 px
        self.resizable(False, False)
        self.transient(padre)                # queda pegado a su ventana, no al menú

        cuerpo = tk.Frame(self, bg=BG_MAIN, padx=22, pady=18)
        cuerpo.pack(fill="both", expand=True, padx=2, pady=2)

        tk.Label(cuerpo, text="✏️  Tu programa pregunta:", font=("Arial", 11, "bold"),
                 bg=BG_MAIN, fg=GRIS, anchor="w").pack(fill="x")
        tk.Label(cuerpo, text=str(pregunta).strip() or "Escribí un valor:",
                 font=("Arial", 14, "bold"), bg=BG_MAIN, fg=BLANCO,
                 anchor="w", justify="left", wraplength=420).pack(fill="x", pady=(4, 12))

        self.entrada = tk.Entry(cuerpo, font=("Consolas", 14), bg=BG_EDITOR, fg=BLANCO,
                                insertbackground=BLANCO, relief=tk.FLAT, width=32,
                                highlightthickness=2, highlightbackground=BG_CARD,
                                highlightcolor=VERDE_BTN)
        self.entrada.pack(fill="x", ipady=6)

        botones = tk.Frame(cuerpo, bg=BG_MAIN)
        botones.pack(fill="x", pady=(14, 0))
        tk.Button(botones, text="✔  Responder", font=("Arial", 12, "bold"), bg=VERDE_BTN,
                  fg="white", activebackground="#15803d", activeforeground="white",
                  relief=tk.FLAT, padx=16, pady=5, cursor="hand2",
                  command=self._aceptar).pack(side=tk.RIGHT)
        tk.Button(botones, text="Cancelar", font=("Arial", 11), bg="#475569", fg="white",
                  activebackground="#334155", activeforeground="white",
                  relief=tk.FLAT, padx=12, pady=5, cursor="hand2",
                  command=self._cancelar).pack(side=tk.RIGHT, padx=(0, 8))
        tk.Label(botones, text="Enter para responder", font=("Arial", 9),
                 bg=BG_MAIN, fg=GRIS).pack(side=tk.LEFT)

        # Se escucha en el propio campo de texto (donde está el foco) y en la ventana
        for widget in (self.entrada, self):
            widget.bind("<Key>", self._tecla, add="+")
        self.bind("<Escape>", self._cancelar)
        self.protocol("WM_DELETE_WINDOW", self._cancelar)

        self._posicionar(padre)
        self.deiconify()
        self.lift(padre)
        self.entrada.focus_force()
        try:
            self.grab_set()                  # modal: no se puede tocar el resto mientras pregunta
        except tk.TclError:
            pass

    def _posicionar(self, padre):
        self.update_idletasks()
        ancho, alto = self.winfo_reqwidth(), self.winfo_reqheight()
        try:
            x = padre.winfo_rootx() + (padre.winfo_width() - ancho) // 2
            y = padre.winfo_rooty() + (padre.winfo_height() - alto) // 3
        except tk.TclError:
            x = (self.winfo_screenwidth() - ancho) // 2
            y = (self.winfo_screenheight() - alto) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _tecla(self, evento):
        logger.info("tecla en preguntar: keysym=%s keycode=%s char=%r state=%s",
                    evento.keysym, evento.keycode, evento.char, evento.state)
        if (evento.keysym in _TECLAS_ENTER or evento.keycode in _CODIGOS_ENTER
                or evento.char in ("\r", "\n")):
            self._aceptar()
            return "break"
        return None

    def _aceptar(self, _evento=None):
        if self.respuesta is not None or not self.winfo_exists():
            return
        self.respuesta = self.entrada.get()
        self.destroy()

    def _cancelar(self, _evento=None):
        self.respuesta = None
        self.destroy()


def preguntar(pregunta, padre=None):
    """Muestra la ventanita y espera la respuesta. Devuelve el texto o None si se cancela."""
    if padre is None:
        padre = _ventana_activa()
    dialogo = DialogoPreguntar(padre, pregunta)
    padre.wait_window(dialogo)
    return dialogo.respuesta


def _ventana_activa():
    """Ventana donde está el foco (desde donde se tocó Ejecutar); si no, la principal."""
    raiz = tk._default_root
    if raiz is None:
        raiz = tk.Tk()
        raiz.withdraw()
        return raiz
    foco = raiz.focus_get()
    return foco.winfo_toplevel() if foco is not None else raiz
