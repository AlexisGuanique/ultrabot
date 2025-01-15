import os
import pyperclip
import pyautogui
import time
from database import get_cookie_by_id


# ? Funcion para manejar el ingreso de la cookie y solicitus del dato a la base de datos
def find_and_click_input():
    input_image_path = "images/inputArea.png"

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

        time.sleep(0.1)

        pyautogui.hotkey("ctrl", "a")
        print("Todo el texto seleccionado.")

        pyautogui.press("delete")
        print("Texto eliminado del input.")

        cookie_id = 2
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


def verify_window(window_image_path, close_button_image_path, confidence=0.8):
    """
    Verifica si hay una ventana específica visible en pantalla y cierra la ventana si se detecta.
    Retorna True si se cerró la ventana, False si no se detectó.
    Si ocurre un error, lo maneja silenciosamente y continúa el flujo.
    """
    try:
        # Intentar localizar la ventana específica
        location = pyautogui.locateCenterOnScreen(
            window_image_path, confidence=confidence)
        if location:
            print(f"Ventana detectada: {window_image_path} en {location}.")

            # Intentar localizar el botón de cerrar ventana
            close_location = pyautogui.locateCenterOnScreen(
                close_button_image_path, confidence=confidence)
            if close_location:
                pyautogui.click(close_location)
                print(
                    f"Ventana cerrada: {close_button_image_path} en {close_location}.")
                return True  # Indica que la ventana fue cerrada
            else:
                print(
                    f"Botón de cerrar no encontrado para la ventana: {window_image_path}.")
        else:
            print(f"Ventana no detectada: {window_image_path}.")
    except Exception as e:
        # Manejar cualquier excepción silenciosamente
        print(f"Error al verificar ventana: {e}. Continuando con el flujo.")

    # No se detectó ninguna ventana o no se pudo cerrar
    return False


def verify_catchat():
    return verify_window("images/catchatAutenticacion.png", "images/cerrarVentana.png")


def verify_login():
    return verify_window("images/logueoUsuarioContrasena.png", "images/cerrarVentana.png")


def verify_verification_code():
    return verify_window("images/codigoVerificacion.png", "images/cerrarVentana.png")


def handle_verifications():
    """
    Maneja las verificaciones de ventanas como captcha, login y código de verificación.
    Retorna True si alguna ventana fue cerrada y se debe reiniciar el flujo, de lo contrario False.
    """
    if verify_catchat():
        print("Se detectó un captcha.")
        return True

    if verify_login():
        print("Se detectó un login.")
        return True

    if verify_verification_code():
        print("Se detectó un código de verificación.")
        return True

    return False


def click_image(image_path, confidence=0.8, offset_x=0, offset_y=0, description=""):
    """
    Busca una imagen en pantalla y hace clic en ella. Continúa si no la encuentra.
    """
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence)
        if location:
            click_x = location[0] + offset_x
            click_y = location[1] + offset_y
            pyautogui.click(click_x, click_y)
            print(f"Clic realizado en {description} ({click_x}, {click_y}).")
            return True  # Indica que se hizo clic exitosamente
        else:
            print(
                f"{description} no encontrada en pantalla. Continuando con el flujo.")
            return False  # Indica que no se encontró la imagen
    except Exception as e:
        print(f"Error al intentar hacer clic en {description}: {e}")
        return False  # Continúa el flujo incluso si ocurre un error inesperado

# Funciones específicas para cada acción


def click_ultra_logo():
    return click_image("images/ultraLogo.png", description="logo de ultra")


def click_add_account():
    return click_image("images/agregarCuenta.png", description="botón de agregar cuenta")


def click_panel_dropdown():
    return click_image("images/panelDesplegable.png", description="panel desplegable")


def click_panel_dropdown2():
    return click_image("images/panelDesplegableTest.png", description="panel desplegable")


def click_add_cookie():
    return click_image("images/ingresarCookies.png", description="botón de agregar cookie")


def click_ok_button():
    return click_image("images/botonOk.png", description="botón Ok")


def click_confirm_user():
    return click_image("images/confirmarUsuario.png", offset_y=120, description="confirmar usuario")


def click_menu_me():
    return click_image("images/menuDesplegableMe.png", description="menú desplegable Me")


def click_sign_out():
    return click_image("images/signOut.png", description="botón de cerrar sesión")


def click_join_now():
    return click_image("images/imagesTest/uneteAhoraTest.png", description="botón de Unete Ahora")


def click_login_test():
    return click_image("images/imagesTest/abc123.png", description="botón de iniciar sesión")


def click_confirm_user_test():
    return click_image("images/imagesTest/confirmarUsuarioTest.png", offset_y=120, description="confirmar usuario test")


def click_minimize_window():
    return click_image("images/minimizarVentana.png", description="botón de minimizar ventana")


def complete_logout_sequence():
    print("Iniciando secuencia de logout...")

    try:
        if not click_panel_dropdown2():
            print("No se encontró el panel desplegable.")
        time.sleep(2)

        if not click_menu_me():
            print("No se encontró el menú 'Me'.")
        time.sleep(1)

        if not click_sign_out():
            print("No se encontró botón de cerrar sesión.")
        time.sleep(3)

        if not click_join_now():
            print("No se encontró botón de Unete Ahora.")
        time.sleep(3)

        if not click_login_test():
            print("No se encontró botón de Iniciar Sesión.")
        time.sleep(7)

        if not click_confirm_user_test():
            print("No se encontró botón de Confirmar Usuario.")
        time.sleep(7)

        if not click_minimize_window():
            print("No se encontró botón de Minimizar Ventana.")
        time.sleep(1)

        print("Secuencia completada por el Ultra Bot.")
        return True

    except Exception as e:
        print(f"Error inesperado durante la secuencia de logout: {e}")
        return False


def execute_ultra_bot():

    click_ultra_logo()
    time.sleep(9)

    while True:

        click_add_account()
        time.sleep(10)

        click_panel_dropdown()
        time.sleep(1)

        click_add_cookie()
        time.sleep(1)

        find_and_click_input()
        time.sleep(1)

        click_ok_button()
        time.sleep(30)

        # Manejar todas las verificaciones
        print("Hasta qui llegue1 ")
        if handle_verifications():
            print("Reiniciando flujo desde agregar cuenta...")
            continue

        print("Hasta aqui llegue 2")
        if complete_logout_sequence():
            continue

        click_confirm_user()
        time.sleep(10)

        # Manejar todas las verificaciones
        if handle_verifications():
            print("Reiniciando flujo desde agregar cuenta...")
            continue

        complete_logout_sequence()
        print("Secuencia completada por el Ultra Bot.")
        break
