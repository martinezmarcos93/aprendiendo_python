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
