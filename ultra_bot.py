import os
import pyperclip
import pyautogui
import time
from database import get_cookie_by_id


last_cookie_id = 1
last_cookie_text = None


def find_and_click_input():
    global last_cookie_id, last_cookie_text

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

        pyautogui.press("delete")

        # Obtener la cookie actual de la base de datos
        cookie_text = get_cookie_by_id(last_cookie_id)

        if cookie_text:
            cookie_text_cleaned = str(cookie_text)

           # Comparar con la última cookie
            if last_cookie_text is not None:
                if cookie_text_cleaned == last_cookie_text:
                    print(f"Cookie ID {last_cookie_id} es IGUAL a la anterior.")
                else:
                    print(f"Cookie ID {last_cookie_id} es DIFERENTE a la anterior.")
            else:
                print("Esta es la primera cookie procesada.")

            # Actualizar la última cookie y copiar al portapapeles
            last_cookie_text = cookie_text_cleaned
            pyperclip.copy(cookie_text_cleaned)
            print(f"Texto de la cookie con ID {last_cookie_id} copiado al portapapeles.")
            pyautogui.hotkey("ctrl", "v")
            print("Texto pegado en el input.")

            # Incrementar el ID para la próxima ejecución
            last_cookie_id += 1
        else:
            print(f"No se pudo obtener la cookie con ID {last_cookie_id}. Deteniendo el flujo.")
            return False  # Indica que ya no hay más cookies y el bucle debe detenerse
    else:
        print("InputArea no encontrada en pantalla. Asegúrate de que sea visible.")

    return True  # Indica que la ejecución fue exitosa


def verify_window(window_image_path, close_button_image_path, confidence=0.8):

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

def verify_login_password():
    return verify_window("images/logueoUsuarioContrasena2.png", "images/cerrarVentana.png")

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

    if verify_login_password():
        print("Se detectó login con contraseña.")
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


def click_image_multiple(image_paths, confidence=0.8, offset_x=0, offset_y=0, description=""):

    for image_path in image_paths:
        try:
            location = pyautogui.locateCenterOnScreen(
                image_path, confidence=confidence)
            if location:
                click_x = location[0] + offset_x
                click_y = location[1] + offset_y
                pyautogui.click(click_x, click_y)
                print(
                    f"Clic realizado en {description} con imagen '{image_path}' en ({click_x}, {click_y}).")
                return True  # Detenemos la búsqueda tras el primer clic exitoso
        except Exception as e:
            print(f"Error al intentar buscar imagen '{image_path}': {e}")

    print(
        f"No se encontró ninguna de las imágenes para {description}: {image_paths}.")
    return False  # No se encontró ninguna imagen


# Funciones específicas para cada acción


def click_ultra_logo():
    return click_image_multiple(["images/ultraLogo.png", "images/ultraLogo2.png"], description="logo de ultra")


def click_add_account():
    return click_image_multiple(["images/agregarCuenta.png", "images/agregarCuentaIngles.png"], description="botón de agregar cuenta")


def click_panel_dropdown():
    return click_image("images/panelDesplegable.png", description="panel desplegable")


def click_panel_dropdown2():
    return click_image("images/panelDesplegableTest.png", description="panel desplegable")


def click_add_cookie():
    return click_image("images/ingresarCookies.png", description="botón de agregar cookie")


def click_ok_button():
    return click_image("images/botonOk.png", description="botón Ok")


def click_menu_me():
    return click_image_multiple(["images/menuDesplegableMe.png", "images/menuDesplegableYo.png"], description="menú desplegable Me")


def click_sign_out():
    return click_image_multiple(["images/signOut.png", "images/signOutEspanol.png"], description="botón de cerrar sesión")


def click_join_now():
    return click_image_multiple(["images/imagesTest/uneteAhoraTest.png", "images/joinNow.png"], description="botón de Unete Ahora")


def click_login():
    return click_image_multiple(["images/imagesTest/abc123.png", "images/singin.png"], description="botón de iniciar sesión")


def click_confirm_user():
    return click_image_multiple(["images/imagesTest/confirmarUsuarioTest.png", "images/confirmarUsuario.png"], offset_y=120, description="confirmar usuario test")


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

        if not click_login():
            print("No se encontró botón de Iniciar Sesión.")
        time.sleep(7)

        if not click_confirm_user():
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

        click_confirm_user()
        time.sleep(5)

        print("Hasta aqui llegue 2")
        if complete_logout_sequence():
            continue

        click_confirm_user()
        time.sleep(15)

        # Manejar todas las verificaciones
        if handle_verifications():
            print("Reiniciando flujo desde agregar cuenta...")
            continue

        complete_logout_sequence()
        print("Secuencia completada por el Ultra Bot.")
        break
