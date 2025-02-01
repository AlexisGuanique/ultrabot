import pyautogui
import time

print("Mueve el mouse y haz clic izquierdo para obtener las coordenadas. Presiona Ctrl+C para salir.")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Posición actual del mouse: ({x}, {y})", end="\r")  # Se actualiza en la misma línea
        time.sleep(0.1)  # Evita que la terminal se sature con prints
except KeyboardInterrupt:
    print("\nScript detenido.")
