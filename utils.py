import tkinter as tk


def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana en el área de trabajo real (sin barra de tareas).
    Funciona correctamente con DPI scaling en Windows.
    """
    ventana.update_idletasks()

    # winfo_screenwidth/height devuelven píxeles físicos en Windows con DPI scaling.
    # Para obtener el área de trabajo disponible usamos la geometría del escritorio.
    pantalla_w = ventana.winfo_screenwidth()
    pantalla_h = ventana.winfo_screenheight()

    # Intentar obtener el área útil real desde el sistema operativo
    try:
        import ctypes
        # RECT: left, top, right, bottom del área de trabajo (sin barra de tareas)
        class RECT(ctypes.Structure):
            _fields_ = [("left",   ctypes.c_long),
                        ("top",    ctypes.c_long),
                        ("right",  ctypes.c_long),
                        ("bottom", ctypes.c_long)]
        rect = RECT()
        # SystemParametersInfoW con SPI_GETWORKAREA (0x0030)
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
        area_w = rect.right  - rect.left
        area_h = rect.bottom - rect.top
        offset_x = rect.left
        offset_y = rect.top
    except Exception:
        # Fallback para macOS / Linux: restar estimación de barra de tareas
        area_w   = pantalla_w
        area_h   = pantalla_h - 60
        offset_x = 0
        offset_y = 0

    ancho_final = min(ancho, area_w  - 20)
    alto_final  = min(alto,  area_h  - 20)

    x = offset_x + (area_w  - ancho_final) // 2
    y = offset_y + (area_h  - alto_final)  // 2

    ventana.geometry(f"{ancho_final}x{alto_final}+{x}+{y}")
    ventana.minsize(min(860, ancho_final), min(480, alto_final))


def habilitar_rueda(canvas):
    """Scroll con la rueda del mouse sobre `canvas` en Windows, macOS y Linux.

    Linux (X11) no manda <MouseWheel> sino <Button-4>/<Button-5>. Se enlaza solo
    mientras el puntero está encima, así no queda un bind_all vivo al cerrar.
    """
    def _rueda(event):
        if getattr(event, "num", None) == 4:
            paso = -1
        elif getattr(event, "num", None) == 5:
            paso = 1
        else:
            paso = -1 if event.delta > 0 else 1
        canvas.yview_scroll(paso, "units")

    def _entrar(_):
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            canvas.bind_all(secuencia, _rueda)

    def _salir(_):
        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            canvas.unbind_all(secuencia)

    canvas.bind("<Enter>", _entrar)
    canvas.bind("<Leave>", _salir)
    canvas.bind("<Destroy>", _salir, add="+")
