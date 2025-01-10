from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
import time

def execute_ultra_bot():
    """Ejecuta un flujo complejo: clics y escritura automática."""
    mouse = MouseController()
    keyboard = KeyboardController()

    # Paso 1: Clic en la primera posición
    first_position = (431.6875, 867.51171875)
    mouse.position = first_position
    time.sleep(1)  # Esperar 1 segundo
    mouse.click(Button.left, 1)  # Realizar clic izquierdo
    print(f"Clic realizado en la posición {first_position}")

    # Paso 2: Clic en la segunda posición
    second_position = (119.77734375, 245.2421875)
    mouse.position = second_position
    time.sleep(1)  # Esperar 1 segundo
    mouse.click(Button.left, 1)  # Realizar clic izquierdo
    print(f"Clic realizado en la posición {second_position}")

    # Paso 3: Escribir el texto
    time.sleep(1)  # Esperar 1 segundo antes de escribir
    text_to_type = "Hola Cabuya, este texto lo envio el Ultra Bot de manera automatica"
    keyboard.type(text_to_type)
    print(f"Texto enviado: {text_to_type}")

    # Paso 4: Clic en la tercera posición
    third_position = (1398.6953125, 809.09765625)
    mouse.position = third_position
    time.sleep(1)  # Esperar 1 segundo
    mouse.click(Button.left, 1)  # Realizar clic izquierdo
    print(f"Clic realizado en la posición {third_position}")

    print("Secuencia completada por el Ultra Bot.")
