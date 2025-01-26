import os
import pyperclip
import pyautogui
import time
from database import get_cookie_by_id, get_password_by_id


last_cookie_id = 4
last_cookie_text = None


def find_and_click_password():
    global last_cookie_id

    # Lista de rutas de imágenes para buscar el campo de contraseña
    password_image_paths = [
        "images/loginPassword/loginPasswordInput.png",
        "images/loginPassword/loginPasswordInputEnglish.png",
        "images/loginPassword/loginPasswordInputSinFocus.png",
        "images/loginPassword/loginPasswordInputSinFocusEnglish.png"
    ]

    password_location = None

    # Buscar la imagen en la pantalla
    for image_path in password_image_paths:
        try:
            password_location = pyautogui.locateCenterOnScreen(
                image_path, confidence=0.8
            )
            if password_location is not None:
                break
        except Exception as e:
            print(f"Error al buscar la imagen {image_path}: {e}")

    if password_location is not None:
        try:
            # Clic exactamente en la posición detectada
            pyautogui.click(password_location)

            # Limpiar el campo de texto
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")

            # Obtener el password actual de la base de datos
            password = get_password_by_id(last_cookie_id)

            if password:
                # Copiar el password al portapapeles
                pyperclip.copy(password)
                print("########################################################")
                print(f"Contraseña con ID {
                      last_cookie_id} copiada al portapapeles.")
                # print(f"Contraseña: {password}")
                print("########################################################")

                # Pegar la contraseña en el campo
                pyautogui.hotkey("ctrl", "v")

            else:
                return False  # Indica que ya no hay más contraseñas y el bucle debe detenerse
        except Exception as e:
            print(f"Error al realizar acciones en la ubicación detectada: {e}")
            return False
    else:
        print(
            "Campo de contraseña no encontrado en pantalla. Asegúrate de que sea visible.")

    print("Búsqueda de contraseña completada. Retornando True.")
    return True  # Indica que la ejecución fue exitosa


def find_and_click_input():
    global last_cookie_id, last_cookie_text

    input_image_paths = ["images/inputArea/inputArea.png",
                         "images/inputArea/inputArea2.png"]

    # Buscar cualquiera de las dos imágenes
    input_location = None
    for image_path in input_image_paths:
        input_location = pyautogui.locateCenterOnScreen(
            image_path, confidence=0.8)
        if input_location is not None:
            print(f"Imagen encontrada: {image_path} en {input_location}")
            break

    if input_location is not None:
        print(f"InputArea encontrada en {
              input_location}. Preparando clic más abajo...")

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
                    print(f"Cookie ID {
                          last_cookie_id} es IGUAL a la anterior.")
                else:
                    print(f"Cookie ID {
                          last_cookie_id} es DIFERENTE a la anterior.")
            else:
                print("Esta es la primera cookie procesada.")

            # Actualizar la última cookie y copiar al portapapeles
            last_cookie_text = cookie_text_cleaned
            pyperclip.copy(cookie_text_cleaned)
            print("########################################################")
            print(f"Texto de la cookie con ID {
                  last_cookie_id} copiado al portapapeles.")
            print("########################################################")

            pyautogui.hotkey("ctrl", "v")

            # Incrementar el ID para la próxima ejecución
            # last_cookie_id += 1
        else:
            print(f"No se pudo obtener la cookie con ID {
                  last_cookie_id}. Deteniendo el flujo.")
            return False  # Indica que ya no hay más cookies y el bucle debe detenerse
    else:
        print("InputArea no encontrada en pantalla. Asegúrate de que sea visible.")

    return True  # Indica que la ejecución fue exitosa


#! Verificacion de catchat
def close_catchat():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/catchatAutenticacion.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el catchat
    except Exception:
        pass
    return False  # No se cerró el catchat


def close_catchat_espanol():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/catchatAutenticacion2.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el catchat en español
    except Exception:
        pass
    return False  # No se cerró el catchat en español


def close_logueo():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/logueoUsuarioContrasena.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el logueo
    except Exception:
        pass
    return False  # No se cerró el logueo


def close_logueo_english():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/logueoUsuarioContrasenaEnglish.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el logueo en inglés
    except Exception:
        pass
    return False  # No se cerró el logueo en inglés


def close_codigo():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/codigoVerificacion.png", confidence=1)
        print(location)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/recargarPestana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el código de verificación
    except Exception:
        pass
    return False  # No se cerró el código de verificación


def close_codigo_espanol():
    try:
        location = pyautogui.locateCenterOnScreen(
            "images/codigoVerificacionEspanol.png", confidence=0.8)
        print(location)
        if location:
            close_location = pyautogui.locateCenterOnScreen(
                "images/recargarPestana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el código de verificación
    except Exception:
        pass
    return False


def click_image(image_path, confidence=0.8, offset_x=0, offset_y=0, description=""):

    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence)
        if location:
            click_x = location[0] + offset_x
            click_y = location[1] + offset_y
            pyautogui.click(click_x, click_y)
            print(f"Clic realizado en {description} ({click_x}, {click_y}).")
            return True
        else:
            print(
                f"{description} no encontrada en pantalla. Continuando con el flujo.")
            pass
    except Exception as e:
        print(f"Error al intentar hacer clic en {description}: {e}")
        pass
    return False


def click_image_multiple(image_paths, confidence=0.8, offset_x=0, offset_y=0, description=""):
    for image_path in image_paths:
        try:
            location = pyautogui.locateCenterOnScreen(
                image_path, confidence=confidence)
            if location:
                click_x = location[0] + offset_x
                click_y = location[1] + offset_y
                pyautogui.click(click_x, click_y)
                return True  # Detener la búsqueda tras el primer clic exitoso
        except Exception as e:
            pass  # Intención clara de continuar tranquilamente con el siguiente path
    pass  # Intención clara de continuar tranquilamente si no hay éxito
    return False  # Indica que no se realizó ninguna acción


# Funciones específicas para cada acción

def click_ultra_logo():
    return click_image_multiple(["images/ultraLogo/ultraLogo.png", "images/ultraLogo/ultraLogo2.png", "images/ultraLogo/ultraLogo3.png"], description="logo de ultra")


def click_add_account():
    return click_image_multiple(["images/agregarCuenta/agregarCuenta.png", "images/agregarCuenta/agregarCuentaIngles.png", "images/agregarCuenta/agregarCuentaIngles2.png"], description="botón de agregar cuenta")


def click_panel_dropDown():
    return click_image_multiple(["images/panelDesplegableDown/panelDesplegableDown.png", "images/panelDesplegableDown/panelDesplegableDown2.png"], description="panel desplegable")


def click_panel_dropUp():
    return click_image("images/panelDesplegableUp.png", description="panel desplegable")


def click_add_cookie():
    return click_image_multiple(["images/ingresarCookie/ingresarCookies.png", "images/ingresarCookie/ingresarCookies2.png"], description="botón de agregar cookie")


def click_ok_button():
    return click_image_multiple(["images/botonOk/botonOk.png", "images/botonOk/botonOk2.png"], description="botón Ok")


def click_menu_me():
    return click_image_multiple(["images/menuDesplegableMe.png", "images/menuDesplegableYo.png"], description="menú desplegable Me")


def click_sign_out():
    return click_image_multiple(["images/signOut.png", "images/signOutEspanol.png"], description="botón de cerrar sesión")


def click_join_now():
    return click_image_multiple(["images/imagesTest/uneteAhoraTest.png", "images/joinNow.png"], description="botón de Unete Ahora")


#!###############################################################################################
#! SECUENCIA NUEVA


def click_login_whit_email():
    return click_image_multiple(["images/loginPassword/loginPasswordEnglish.png", "images/loginPassword/loginPasswordEspanol.png"], description="botón de iniciar sesión con Email")


def click_close_boton():
    return click_image("images/loginPassword/loginExit.png", description="botón de X de detener el loguin")


def click_sing_in():
    return click_image_multiple(["images/loginPassword/loginPasswordBotonEnglish.png", "images/loginPassword/loginPasswordBotonEspanol.png"], description="botón de iniciar sesión")


def click_remember_me():
    return click_image_multiple(["images/loginPassword/logoutEspanol.png"], description="botón de iniciar sesión")


def click_options_forget_account():
    return click_image_multiple(["images/loginPassword/loginOptions.png"], description="botón de opcion de olvidar cuenta")


def click_forget_account():
    return click_image_multiple(["images/loginPassword/forgetAccount.png", "images/loginPassword/forgetAccountEspanol.png"], description="botón de iniciar sesión")


#!###############################################################################################


def click_confirm_user():
    return click_image_multiple(["images/imagesTest/confirmarUsuarioTest.png", "images/confirmarUsuario.png"], offset_y=120, description="confirmar usuario test")


def click_minimize_window():
    return click_image("images/minimizarVentana.png", description="botón de minimizar ventana")


def click_refresh():
    return click_image("images/recargarPestana.png", description="botón de recargar ventana")


def click_refresh_location():
    print("Recargando la ubicación...")


def move_mouse_down(pixels=100, duration=0.5):
    try:
        current_x, current_y = pyautogui.position()

        new_y = current_y + pixels

        pyautogui.moveTo(current_x, new_y, duration=duration)
        print(f"Mouse movido hacia abajo a la posición ({
              current_x}, {new_y}).")
    except Exception as e:
        print(f"Error al mover el mouse: {e}")


#! FUNCION PRIINCIPAL


def execute_ultra_bot():
    global last_cookie_id
    print("########################################################################")
    print("INICIANDO EL BOT ULTRA")
    print("########################################################################")
    click_ultra_logo()
    time.sleep(4)

    def execute_from_login_with_email():
        """Ejecuta las acciones desde 'click_login_with_email'."""

        if not click_options_forget_account():
            return
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        click_login_whit_email()
        time.sleep(1.5)

        click_close_boton()
        print("Estoy aquí, ya pasé el botón de detener el login")

        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()
        print("Estoy aquí, ya copié y pegué el password")

        time.sleep(3)
        click_sing_in()
        print("Estoy aquí, ya inició sesión")

    def deslogin():
        if not click_login_whit_email():
            return
        time.sleep(1.5)

        click_close_boton()
        print("Estoy aquí, ya pasé el botón de detener el login")

        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()
        print("Estoy aquí, ya copié y pegué el password")

        time.sleep(3)
        click_sing_in()
        print("Estoy aquí, ya inició sesión")

    def login_direct():
        if not click_menu_me():
            return
        time.sleep(3)

        click_sign_out()
        time.sleep(3)

        click_remember_me()
        time.sleep(5)

        click_login_whit_email()
        time.sleep(1.5)

        click_close_boton()
        print("Estoy aquí, ya pasé el botón de detener el login")

        time.sleep(3)
        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()
        print("Estoy aquí, ya copié y pegué el password")

        time.sleep(3)
        click_sing_in()
        print("Estoy aquí, ya inició sesión")

    def request_password():

        if not find_and_click_password():
            print("Estoy aquí, ya copié y pegué el password")
            return

        time.sleep(3)
        click_sing_in()

    while True:

        print("Estoy aqui ya entre al bucle")

        click_add_account()
        time.sleep(10)

        click_panel_dropDown()
        time.sleep(2)

        click_add_cookie()
        time.sleep(2)

        find_and_click_input()
        time.sleep(2)

        click_ok_button()
        time.sleep(2)

        click_refresh()
        time.sleep(2)

        move_mouse_down(pixels=150, duration=0.7)
        time.sleep(30)

        print("########################################################################")
        print("Pasaron los 40 segundos. Iniciando variantes")
        print("########################################################################")

        #!#######################################################################

        login_direct()
        time.sleep(3)

        request_password()
        time.sleep(3)

        execute_from_login_with_email()
        time.sleep(3)

        deslogin()
        time.sleep(3)


        if close_codigo():
            print("Código de verificación detectado y reiniciando.")
            deslogin()
        else:
            click_minimize_window()
            last_cookie_id += 1
            continue 
        time.sleep(3)

        if close_codigo_espanol():
            print("Código de verificación detectado y reiniciando.")
            deslogin()  
        else:
            click_minimize_window()
            last_cookie_id += 1
            continue
        time.sleep(3)

        #!#######################################################################

        #! Variante 5
        # if close_verifications():
        #     print("Secuencia de variante 5 realizada con exito. Reiniciando el bucle...")
        #     continue
        # time.sleep(8)

        time.sleep(2)
        if close_catchat():
            print("Catchat detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el Catchat
        time.sleep(3)

        if close_catchat_espanol():
            print("Catchat en español detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el Catchat en español
        time.sleep(3)

        if close_logueo():
            print("Logueo detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el logueo
        time.sleep(3)

        if close_logueo_english():
            print("Logueo en inglés detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el logueo en inglés
        time.sleep(3)

        #! variante 1

        #!#######################################################################
        login_direct()
        time.sleep(7)

        if close_codigo():
            print("Código de verificación detectado y cerrado.")
            deslogin()  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)

        if close_codigo_espanol():
            print("Código de verificación detectado y cerrado.")
            deslogin()  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)

        #!#######################################################################
        deslogin()
        time.sleep(8)

        if close_codigo():
            print("Código de verificación detectado y cerrado.")
            deslogin()  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)

        if close_codigo_espanol():
            print("Código de verificación detectado y cerrado.")
            deslogin()  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)
        #!#######################################################################

        if click_minimize_window():
            print("Ventana principal detectada y minimizada.")
            continue
        time.sleep(2)

        #! variante 5

        time.sleep(3)
        if close_catchat():
            print("Catchat detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el Catchat
        time.sleep(3)

        if close_catchat_espanol():
            print("Catchat en español detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el Catchat en español
        time.sleep(3)

        if close_logueo():
            print("Logueo detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el logueo
        time.sleep(3)

        if click_minimize_window():
            print("Ventana principal detectada y minimizada.")
            continue
        time.sleep(2)

        break
