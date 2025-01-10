from pynput.mouse import Listener

def on_click(x, y, button, pressed):
    if pressed:  # Solo mostrar coordenadas cuando se presiona el botón
        print(f"Clic detectado en: ({x}, {y})")

# Listener para rastrear clics
with Listener(on_click=on_click) as listener:
    listener.join()
