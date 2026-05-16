import threading

try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False

def play_sound(tipo):
    if not _HAS_WINSOUND:
        return

    def _play():
        try:
            if tipo == "success":
                # Arpegio ascendente rápido
                winsound.Beep(523, 100) # C5
                winsound.Beep(659, 100) # E5
                winsound.Beep(784, 150) # G5
                winsound.Beep(1046, 300) # C6
            elif tipo == "error":
                # Tono descendente de error
                winsound.Beep(300, 200)
                winsound.Beep(200, 400)
            elif tipo == "level_up":
                # Fanfarria
                winsound.Beep(440, 150)
                winsound.Beep(554, 150)
                winsound.Beep(659, 150)
                winsound.Beep(880, 400)
        except Exception:
            pass
            
    # Ejecutar en hilo separado para no bloquear la UI de Tkinter
    threading.Thread(target=_play, daemon=True).start()
