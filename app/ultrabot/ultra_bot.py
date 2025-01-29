import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id


last_cookie_id = 1
last_cookie_text = None


def find_and_click_password():
    global last_cookie_id

    # Lista de rutas de imágenes para buscar el campo de contraseña
    password_image_paths = [
        "app/ultrabot/images/loginPassword/loginPasswordInput.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocus.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocusEnglish.png"
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
                print(f"Contraseña con ID {last_cookie_id} copiada al portapapeles.")
                print("########################################################")

                # Pegar la contraseña en el campo
                pyautogui.hotkey("ctrl", "v")

                return True  # Indica que la ejecución fue exitosa

            else:
                print("No se encontró una contraseña válida en la base de datos.")
                return False  # Indica que ya no hay más contraseñas y el bucle debe detenerse
        except Exception as e:
            print(f"Error al realizar acciones en la ubicación detectada: {e}")
            return False
    else:
        print(
            "Campo de contraseña no encontrado en pantalla. Asegúrate de que sea visible.")
        return False  # Asegura que siempre retornamos False si no se encuentra el campo


def find_and_click_input():
    global last_cookie_id, last_cookie_text

    input_image_paths = ["app/ultrabot/images/inputArea/inputArea.png",
                         "app/ultrabot/images/inputArea/inputArea2.png"]

    # Buscar cualquiera de las dos imágenes
    input_location = None
    for image_path in input_image_paths:
        input_location = pyautogui.locateCenterOnScreen(
            image_path, confidence=0.8)
        if input_location is not None:
            print(f"Imagen encontrada: {image_path} en {input_location}")
            break

    if input_location is not None:
        print(f"InputArea encontrada en {input_location}. Preparando clic más abajo...")

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
            print("########################################################")
            print(f"Texto de la cookie con ID {last_cookie_id} copiado al portapapeles.")
            print("########################################################")

            pyautogui.hotkey("ctrl", "v")

            # Incrementar el ID para la próxima ejecución
            # last_cookie_id += 1
        else:
            print(f"No se pudo obtener la cookie con ID {last_cookie_id}. Deteniendo el flujo.")
            return False  # Indica que ya no hay más cookies y el bucle debe detenerse
    else:
        print("InputArea no encontrada en pantalla. Asegúrate de que sea visible.")

    return True  # Indica que la ejecución fue exitosa


#! Verificacion de codigo
def close_codigo():
    try:
        # Buscar la ubicación del código de verificación
        location = pyautogui.locateCenterOnScreen(
            "app/ultrabot/images/codigoVerificacion/codigoVerificacion.png", confidence=0.8
        )
        print(f"Ubicación del código de verificación: {location}")

        if location:
            # Buscar la ubicación del botón para cerrar o recargar
            close_location = pyautogui.locateCenterOnScreen(
                "app/ultrabot/images/recargarPestana.png", confidence=0.8
            )
            print(f"Ubicación del botón de recargar: {close_location}")

            if close_location:
                pyautogui.click(close_location)
                print("Se cerró el código de verificación con éxito.")
                return True  
            else:
                print("No se encontró el botón para recargar la pestaña.")
        else:
            print("No se encontró el código de verificación en pantalla.")
    except Exception as e:
        print(f"Error en la función close_codigo: {e}")

    return False  # No se encontró o cerró el código de verificación


def close_codigo_espanol():
    try:
        # Buscar la ubicación del código de verificación en español
        location = pyautogui.locateCenterOnScreen(
            "app/ultrabot/images/codigoVerificacion/codigoVerificacionEspanol.png", confidence=0.8
        )
        print(f"Ubicación del código de verificación en español: {location}")

        if location:
            # Buscar la ubicación del botón para cerrar o recargar
            close_location = pyautogui.locateCenterOnScreen(
                "app/ultrabot/images/recargarPestana.png", confidence=0.8
            )
            print(f"Ubicación del botón de recargar: {close_location}")

            if close_location:
                pyautogui.click(close_location)
                print("Se cerró el código de verificación en español con éxito.")
                return True  # Indica que se cerró correctamente
            else:
                print("No se encontró el botón para recargar la pestaña en español.")
        else:
            print("No se encontró el código de verificación en español en pantalla.")
    except Exception as e:
        print(f"Error en la función close_codigo_espanol: {e}")

    return False  # No se encontró o cerró el código de verificación en español


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
    return click_image_multiple(["app/ultrabot/images/ultraLogo/ultraLogo.png", "app/ultrabot/images/ultraLogo/ultraLogo2.png", "app/ultrabot/images/ultraLogo/ultraLogo3.png", "images/ultraLogo/ultraLogo4.png"], description="logo de ultra")


def click_add_account():
    return click_image_multiple(["app/ultrabot/images/agregarCuenta/agregarCuenta.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles2.png"], description="botón de agregar cuenta")


def click_panel_dropDown():
    return click_image_multiple(["app/ultrabot/images/panelDesplegableDown/panelDesplegableDown.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown2.png"], description="panel desplegable")


def click_add_cookie():
    return click_image_multiple(["app/ultrabot/images/ingresarCookie/ingresarCookies.png", "app/ultrabot/images/ingresarCookie/ingresarCookies2.png"], description="botón de agregar cookie")


def click_ok_button():
    return click_image_multiple(["app/ultrabot/images/botonOk/botonOk.png", "app/ultrabot/images/botonOk/botonOk2.png"], description="botón Ok")


def click_menu_me():
    return click_image_multiple(["app/ultrabot/images/menuDesplegable/menuDesplegableMe.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo.png"], description="menú desplegable Me")


def click_sign_out():
    return click_image_multiple(["app/ultrabot/images/singout/signOut.png", "app/ultrabot/images/singout/signOutEspanol.png"], description="botón de cerrar sesión")


#!###############################################################################################
#! SECUENCIA NUEVA


def click_login_whit_email():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordEnglish.png", "app/ultrabot/images/loginPassword/loginPasswordEspanol.png"], description="botón de iniciar sesión con Email")


def click_close_boton():
    return click_image("app/ultrabot/images/loginPassword/loginExit.png", description="botón de X de detener el loguin")


def click_sing_in():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordBotonEnglish.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEspanol.png"], description="botón de iniciar sesión")


def click_remember_me():
    return click_image_multiple(["app/ultrabot/images/loginPassword/logoutEspanol.png"], description="botón de iniciar sesión")


def click_options_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginOptions.png"], description="botón de opcion de olvidar cuenta")


def click_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/forgetAccount.png", "app/ultrabot/images/loginPassword/forgetAccountEspanol.png"], description="botón de iniciar sesión")


#!###############################################################################################



def click_minimize_window():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/minimizarVentana.png"], description="botón de minimizar ventana")


def click_refresh():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/recargarPestana.png", "app/ultrabot/images/accionesVentana/recargarPestana2.png"], description="botón de recargar ventana")


def click_refresh_location():
    print("Recargando la ubicación...")


def move_mouse_down(pixels=100, duration=0.5):
    try:
        current_x, current_y = pyautogui.position()

        new_y = current_y + pixels

        pyautogui.moveTo(current_x, new_y, duration=duration)
        print(f"Mouse movido hacia abajo a la posición ({current_x}, {new_y}).")
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
        print("Ejecutando funcion que pide confirmacion")

        if not click_options_forget_account():
            print("No se pudo encontrar la opción de los tres puntos, saliendo de la funcion execute_from_login_with_email()")
            return
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        click_login_whit_email()
        time.sleep(1.5)

        click_close_boton()

        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()

        time.sleep(3)
        click_sing_in()

    def deslogin():
        print("Ejecutando funcion cuando se desloguea la cuenta")

        if not click_login_whit_email():
            print(
                "No se pudo encontrar la opción de deslogueo, saliendo de la funcion deslogin()")
            return
        time.sleep(1.5)

        click_close_boton()

        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()

        time.sleep(3)
        click_sing_in()

    def login_direct():
        print("Ejecutando funcion de logueo directo")

        if not click_menu_me():
            print(
                "No se pudo encontrar el botón Me, saliendo de la funcion login_direct()")
            return
        time.sleep(3)

        click_sign_out()
        time.sleep(3)

        click_remember_me()
        time.sleep(5)

        click_login_whit_email()
        time.sleep(1.5)

        click_close_boton()

        time.sleep(3)
        click_options_forget_account()
        time.sleep(3)

        click_forget_account()
        time.sleep(6)

        find_and_click_password()

        time.sleep(3)
        click_sing_in()

    def request_password():
        print("Ejecutando funcion para solicitar contraseña")

        if not find_and_click_password():
            print("No se pudo encontrar el input para solicitar contraseña, saliendo de la funcion request_password()")
            return

        time.sleep(3)
        click_sing_in()

    while True:

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
        time.sleep(40)

        # print("########################################################################")
        print("Pasaron los 40 segundos. Iniciando variantes")
        # print("########################################################################")

        #!#######################################################################

        login_direct()
        time.sleep(3)

        request_password()
        time.sleep(3)

        execute_from_login_with_email()
        time.sleep(3)

        deslogin()
        time.sleep(8)

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

        break
