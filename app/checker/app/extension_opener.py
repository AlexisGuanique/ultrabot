import time
import pyautogui
import pyperclip
from . import element_click_strategies as ecs
from ...database.database import get_coordinates


def openExtensionWithImageClick(driver, imagePath="cookie.png", confidenceLevel=0.8, override_cookie=None):

    coords = get_coordinates()

    if coords:
        cookieEditor, cookieEditorOption, cookieEditionImport, cookieEditorExport, cookieEditorClose = [
            tuple(map(int, coord.split("x"))) for coord in coords
        ]
    else:
        print("❌ No se encontraron coordenadas en la base de datos.")
        return


    try:
        pyautogui.moveTo(cookieEditor[0], cookieEditor[1], duration=0.3)

        pyautogui.rightClick()
        print(
            f"Right-clicked extension icon at: ({cookieEditor[0]}, {cookieEditor[1]})")
    except Exception as e:
        print(f"Error right-clicking extension icon: {e}")

    time.sleep(1)  # Espera a que se despliegue el popup de la extensión

    # Paso 2: Clic izquierdo en la posición determinada.
    try:
        x2, y2 = 1121, 324  # Coordenadas para el clic izquierdo
        pyautogui.moveTo(
            cookieEditorOption[0], cookieEditorOption[1], duration=0.3)
        pyautogui.click()
        print(f"Left-clicked at: ({x2}, {y2})")
    except Exception as e:
        print(f"Error left-clicking at: {e}")

    time.sleep(1)  # Espera para que se muestre el input del popup.

    try:
        # Coordenadas del botón "Import" (ajusta según tu pantalla)
        pyautogui.moveTo(
            cookieEditionImport[0], cookieEditionImport[1], duration=0.3)
        pyautogui.click()
        print(
            f"Clicked 'Import' button at: ({cookieEditionImport[0]}, {cookieEditionImport[1]})")
    except Exception as e:
        print(f"Error clicking 'Import' button: {e}")

    time.sleep(0.9)  # Espera para que se muestre el input del popup.

    # 🔹 Usamos la cookie que viene por parámetro
    try:
        text_content = override_cookie
        pyperclip.copy(text_content)
        pyautogui.hotkey("ctrl", "v")  # ctrl para Windows
        print("Texto pegado mediante hotkey (Ctrl+V).")
    except Exception as e:
        print(f"Error al pegar el texto: {e}")

    time.sleep(1)

    try:
        pyautogui.moveTo(
            cookieEditorExport[0], cookieEditorExport[1], duration=0.3)
        pyautogui.click()
        print(
            f"Final click at: ({cookieEditorExport[0]}, {cookieEditorExport[1]})")
    except Exception as e:
        print(f"Error en el clic final: {e}")

    time.sleep(1.5)

    # Paso 6: Refrescar la ventana usando Selenium.
    try:
        for i in range(3):
            driver.refresh()
            print(f"🔄 Refresh {i+1} realizado.")
            time.sleep(1.5)
    except Exception as e:
        print(f"❌ Error al refrescar la ventana: {e}")

    time.sleep(6)


    # 1. Verificar si hay que abortar primero
    if ecs.should_abort_session(driver):
        print("⛔ Se detectó una condición de salida. Siguiente cookie...")
        driver.quit()
        time.sleep(0.5)
        return

    clicked_next = ecs.click_next(driver)
    clicked_refresh = ecs.click_feed_refresh_and_logout(driver)

    process_clicked = clicked_next or clicked_refresh

    # 3. Si nada se ejecutó, informar
    if not process_clicked:
        print("❌ No se realizó ninguna acción automatizada.")
