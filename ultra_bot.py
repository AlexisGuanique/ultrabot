import pyautogui
import time

def execute_ultra_bot():
    # Ruta de la primera imagen
    image_path = "ultraLogo.png"

    # Buscar la primera imagen y hacer clic
    image_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

    if image_location is not None:
        print(f"Primera imagen encontrada en {image_location}. Realizando clic...")
        pyautogui.click(image_location)  # Hacer clic en el centro de la imagen
        print(f"Clic realizado en la primera imagen.")
    else:
        print("Primera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return  # Terminar la ejecución si no encuentra la imagen

    time.sleep(6)

    # Ruta de la segunda imagen
    second_image_path = "agregarCuenta.png"

    # Hacer clic 15 veces en la segunda imagen
    for i in range(15):
        second_image_location = pyautogui.locateCenterOnScreen(second_image_path, confidence=0.8)

        if second_image_location is not None:
            print(f"Segunda imagen encontrada en {second_image_location}. Realizando clic ({i + 1}/15)...")
            pyautogui.click(second_image_location)
            time.sleep(0.1)  # Pausa entre clics para simular un clic humano
        else:
            print("Segunda imagen no encontrada en pantalla. Asegúrate de que sea visible.")
            break  # Detener el ciclo si no encuentra la imagen

    print("Secuencia completada por el Ultra Bot.")

