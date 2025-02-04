import pyautogui
import time
from PIL import ImageGrab

def get_mouse_color():
    """Obtiene el color de la pantalla en las coordenadas actuales del mouse en formato RGBA."""
    try:
        x, y = pyautogui.position()  # Obtener coordenadas actuales del mouse
        screenshot = ImageGrab.grab()  # Capturar pantalla
        color = screenshot.getpixel((x, y))  # Obtener color en las coordenadas
        
        print(f"🎯 Coordenadas: ({x}, {y}) - Color RGBA: {color}")
        return color
    except Exception as e:
        print(f"⚠️ Error obteniendo color: {e}")
        return None

# Llamar a la función en un bucle para ver el color en tiempo real
print("📌 Mueve el mouse y presiona CTRL + C para salir.")
try:
    while True:
        get_mouse_color()
        time.sleep(1)  # Actualiza cada segundo
except KeyboardInterrupt:
    print("\n🔴 Finalizado.")
