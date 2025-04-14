import pyautogui
import time

# Factor de escala para pantallas Retina (ajusta este valor si fuera necesario)
SCALING_FACTOR = 2

def displayMouseCoordinates():
    """
    Muestra en tiempo real las coordenadas lógicas y las físicas del mouse.
    Las coordenadas lógicas son las que devuelve pyautogui.position(), mientras
    que las físicas se calculan multiplicando por el SCALING_FACTOR.
    """
    try:
        while True:
            # Coordenadas lógicas (en puntos)
            x, y = pyautogui.position()
            # Coordenadas físicas (en píxeles) aplicando el factor de escala
            physical_x = x * SCALING_FACTOR
            physical_y = y * SCALING_FACTOR
            
            print(
                f"Logical: X = {x}, Y = {y}  |  Physical: X = {physical_x}, Y = {physical_y}",
                end="\r"
            )
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPrograma terminado.")

if __name__ == "__main__":
    displayMouseCoordinates()
