import pyperclip
import pyautogui
import time
# Asegúrate de importar tu función de base de datos
from database import get_cookie_by_id


def find_and_click_input():
    # Ruta de la imagen del área del input
    input_image_path = "images/inputArea.png"

    # Buscar la imagen del área del input en la pantalla
    input_location = pyautogui.locateCenterOnScreen(
        input_image_path, confidence=0.8)

    if input_location is not None:
        print(
            f"InputArea encontrada en {input_location}. Preparando clic más abajo...")

        offset_y = 100
        click_x = input_location[0]
        click_y = input_location[1] + offset_y

        pyautogui.click(click_x, click_y)
        print(f"Clic realizado debajo de InputArea en ({click_x}, {click_y}).")

        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "a")
        print("Todo el texto seleccionado.")

        pyautogui.press("delete")
        print("Texto eliminado del input.")

        cookie_id = 1
        cookie_text = get_cookie_by_id(cookie_id)

        if cookie_text:
            cookie_text_cleaned = str(cookie_text)
            pyperclip.copy(cookie_text_cleaned)
            print("Texto de la cookie copiado al portapapeles.")

            pyautogui.hotkey("ctrl", "v")
            print("Texto pegado en el input.")
        else:
            print(f"No se pudo obtener la cookie con ID {cookie_id}.")
    else:
        print("InputArea no encontrada en pantalla. Asegúrate de que sea visible.")


def execute_ultra_bot():
    # Primera imagen
    image_path = "images/ultraLogo.png"
    image_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

    if image_location is not None:
        print(
            f"Primera imagen encontrada en {image_location}. Realizando clic...")
        pyautogui.click(image_location)
        print(f"Clic realizado en la primera imagen.")
    else:
        print("Primera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    time.sleep(6)

    # Segunda imagen
    second_image_path = "images/agregarCuenta.png"
    for i in range(1):
        second_image_location = pyautogui.locateCenterOnScreen(
            second_image_path, confidence=0.8)

        if second_image_location is not None:
            print(
                f"Segunda imagen encontrada en {second_image_location}. Realizando clic ({i + 1}/5)...")
            pyautogui.click(second_image_location)
            time.sleep(0.1)
        else:
            print(
                "Segunda imagen no encontrada en pantalla. Asegúrate de que sea visible.")
            break

    # Pausa antes de buscar la tercera imagen
    time.sleep(2)

    # Tercera imagen
    quinta_image_path = "images/panelDesplegable.png"
    quinta_image_location = pyautogui.locateCenterOnScreen(
        quinta_image_path, confidence=0.8)

    if quinta_image_location is not None:
        print(
            f"Tercera imagen encontrada en {quinta_image_location}. Realizando clic...")
        pyautogui.click(quinta_image_location)
        print(f"Clic realizado en la tercera imagen.")
    else:
        print("Tercera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    # Pausa antes de buscar la cuarta imagen
    time.sleep(3)

    # Cuarta imagen
    fourth_image_path = "images/ingresarCookies.png"
    fourth_image_location = pyautogui.locateCenterOnScreen(
        fourth_image_path, confidence=0.8)

    if fourth_image_location is not None:
        print(
            f"Cuarta imagen encontrada en {fourth_image_location}. Realizando clic...")
        pyautogui.click(fourth_image_location)
        print(f"Clic realizado en la cuarta imagen.")
    else:
        print("Cuarta imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    # Pausa antes de buscar el input
    time.sleep(3)

    # Buscar y hacer clic en el input
    find_and_click_input()

    time.sleep(3)
    
    # Quinta imagen
    quinta_image_path = "images/botonOk.png"
    quinta_image_location = pyautogui.locateCenterOnScreen(
        quinta_image_path, confidence=0.8)

    if quinta_image_location is not None:
        print(
            f"Tercera imagen encontrada en {quinta_image_location}. Realizando clic...")
        pyautogui.click(quinta_image_location)
        print(f"Clic realizado en la quinta imagen.")
    else:
        print("Tercera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    print("Secuencia completada por el Ultra Bot.")
