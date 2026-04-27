import tkinter as tk


def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana en la pantalla, asegurándose de que
    no quede tapada por la barra de tareas.
    Llama esto DESPUÉS de construir la UI para que el tamaño sea correcto.
    """
    ventana.update_idletasks()

    # Tamaño real de la pantalla
    pantalla_w = ventana.winfo_screenwidth()
    pantalla_h = ventana.winfo_screenheight()

    # Reservar ~48px abajo para la barra de tareas de Windows
    area_util_h = pantalla_h - 48

    # Ajustar si la ventana es más grande que el área útil
    ancho_final = min(ancho, pantalla_w - 20)
    alto_final  = min(alto,  area_util_h - 20)

    x = (pantalla_w  - ancho_final) // 2
    y = (area_util_h - alto_final)  // 2

    ventana.geometry(f"{ancho_final}x{alto_final}+{x}+{y}")
    ventana.minsize(min(900, ancho_final), min(500, alto_final))
