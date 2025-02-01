import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id
import cv2


last_cookie_id = 1
last_cookie_text = None


def find_image(image_path, confidence=0.7):
    """Busca una imagen en la pantalla y devuelve su ubicación si la encuentra."""
    try:
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"⚠️ No se pudo cargar la imagen: {image_path}")
            return None

        # Redimensionar si es demasiado grande
        if template.shape[0] > 500 or template.shape[1] > 500:
            template = cv2.resize(template, (500, 500))
            print(f"🔍 Redimensionando imagen para mejor detección: {
                  image_path}")

        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, grayscale=True)
        if location:
            print(f"✅ Imagen detectada: {image_path} en {location}")
            return location
        else:
            print(f"❌ Imagen no encontrada: {image_path}")

    except Exception as e:
        print(f"⚠️ Error detectando {image_path}: {e}")
    return None


def find_and_click_password():
    global last_cookie_id

    print("🔍 Buscando campo de contraseña...")

    # Lista de imágenes a buscar
    password_images = [
        "app/ultrabot/images/loginPassword/loginPasswordInput.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish2.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish3.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish4.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocus.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocusEnglish.png"
    ]

    # Buscar la imagen en la pantalla
    if any(find_image(image) for image in password_images):
        click_x, click_y = 1332, 650
        print(f"🖱️ Haciendo clic en ({click_x}, {click_y})")

        pyautogui.moveTo(click_x, click_y, duration=0.5)
        time.sleep(0.2)  # Pausa para estabilidad

        pyautogui.mouseDown()
        time.sleep(0.1)  # Asegurar que el clic se registre
        pyautogui.mouseUp()

        # Limpiar el campo de texto
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")

        # Obtener la contraseña de la base de datos
        password = get_password_by_id(last_cookie_id)
        if password:
            pyperclip.copy(password)
            print("########################################################")
            print(f"🔑 Contraseña con ID {
                  last_cookie_id} copiada al portapapeles.")
            print("########################################################")

            # Pegar la contraseña en el campo
            pyautogui.hotkey("ctrl", "v")
            return True  # Ejecución exitosa

    print("❌ No se encontró el campo de contraseña en pantalla.")
    return False  # No se encontró el campo de contraseña


def find_and_click_input():
    global last_cookie_id, last_cookie_text

    input_image_paths = [
        "app/ultrabot/images/inputArea/inputArea.png",
        "app/ultrabot/images/inputArea/inputArea2.png",
        "app/ultrabot/images/inputArea/inputArea3.png"
    ]

    found = False
    for image in input_image_paths:
        try:
            # Verifica si la imagen existe y se puede cargar correctamente
            if cv2.imread(image) is None:
                print(f"⚠️ Imagen no encontrada o inválida: {image}")
                continue

            if pyautogui.locateCenterOnScreen(image, confidence=0.8):
                print(f"✅ Imagen encontrada: {image}")
                found = True
                break
        except Exception as e:
            print(f"⚠️ Error detectando {image}: {e}")

    if not found:
        print("❌ No se encontró ninguna imagen. Continuando con el proceso...")

    # Siempre hacer clic en (1272, 612)
    click_x, click_y = 1272, 612
    print(f"🖱️ Clic en ({click_x}, {click_y})")
    pyautogui.moveTo(click_x, click_y, duration=0.5)
    time.sleep(0.2)
    pyautogui.click()

    # Limpiar input
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")

    # Obtener y pegar cookie
    cookie_text = get_cookie_by_id(last_cookie_id)
    if cookie_text:
        print(f"🍪 Cookie ID {last_cookie_id} procesada.")
        last_cookie_text = cookie_text
        pyperclip.copy(cookie_text)
        pyautogui.hotkey("ctrl", "v")

    return True  # La función sigue ejecutándose sin interrupciones


#! Verificacion de codigo


def close_codigo(espanol=False):
    print(f"🔍 Buscando código de verificación {
          'en español' if espanol else ''}...")

    images = [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion.png",
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion2.png"
    ] if not espanol else [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacionEspanol.png"
    ]

    if any(find_image(image) for image in images):
        click_x, click_y = 1246, 220
        print(f"🖱️ Moviendo mouse y haciendo clic en ({click_x}, {click_y})")

        pyautogui.moveTo(click_x, click_y, duration=0.5)
        time.sleep(0.2)

        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()

        return True

    print("❌ No se encontró ninguna imagen.")
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


def click_image_multiple(image_paths, description="", fallback_coords=None):
    """Busca imágenes en pantalla y si encuentra alguna, hace clic en las coordenadas proporcionadas."""
    print(description)

    for image in image_paths:
        if find_image(image):
            if fallback_coords:
                try:
                    x, y = map(int, fallback_coords.split(" x "))
                    print(f"✅ Imagen detectada. Haciendo clic en ({x}, {y})")
                    pyautogui.moveTo(x, y, duration=0.5)
                    time.sleep(0.2)
                    pyautogui.mouseDown()
                    time.sleep(0.1)
                    pyautogui.mouseUp()
                    return True
                except ValueError:
                    print(f"⚠️ Coordenadas inválidas: '{fallback_coords}'")
    print("❌ No se encontró ninguna imagen. Continuando con el código.")
    return False

#! Funciones específicas para cada acción


def click_ultra_logo():
    return click_image_multiple(["app/ultrabot/images/ultraLogo/ultraLogo.png", "app/ultrabot/images/ultraLogo/ultraLogo2.png", "app/ultrabot/images/ultraLogo/ultraLogo3.png", "app/ultrabot/images/ultraLogo/ultraLogo4.png"], description="Logo de ultra", fallback_coords="642 x 1492")


def click_add_account():
    return click_image_multiple(["app/ultrabot/images/agregarCuenta/agregarCuenta.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles2.png"], description="botón de agregar cuenta", fallback_coords="2492 x 324")


def click_panel_dropDown():
    return click_image_multiple(["app/ultrabot/images/panelDesplegableDown/panelDesplegableDown.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown2.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown3.png"], description="panel desplegable", fallback_coords="1170 x 186")


def click_add_cookie():
    return click_image_multiple(["app/ultrabot/images/ingresarCookie/ingresarCookies.png", "app/ultrabot/images/ingresarCookie/ingresarCookies2.png", "app/ultrabot/images/ingresarCookie/ingresarCookies3.png"], description="botón de agregar cookie", fallback_coords="1368 x 220")


def click_ok_button():
    return click_image_multiple(["app/ultrabot/images/botonOk/botonOk.png", "app/ultrabot/images/botonOk/botonOk2.png", "app/ultrabot/images/botonOk/botonOk3.png"], description="botón Ok", fallback_coords="2170 x 900")


def click_menu_me():
    return click_image_multiple(["app/ultrabot/images/menuDesplegable/menuDesplegableMe.png","app/ultrabot/images/menuDesplegable/menuDesplegableMe2.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo.png"], description="menú desplegable Me", fallback_coords="1958 x 326")


def click_sign_out():
    return click_image_multiple(["app/ultrabot/images/singout/signOut.png", "app/ultrabot/images/singout/signOut2.png", "app/ultrabot/images/singout/signOutEspanol.png"], description="botón de cerrar sesión", fallback_coords="1522 x 1158")


#!###############################################################################################
#! SECUENCIA NUEVA


def click_login_whit_email():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordEnglish.png", "app/ultrabot/images/loginPassword/loginPasswordEnglish2.png", "app/ultrabot/images/loginPassword/loginPasswordEspanol.png"], description="botón de iniciar sesión con Email", fallback_coords="624 x 958")


def click_close_boton():
    return click_image("app/ultrabot/images/loginPassword/loginExit.png", description="botón de X de detener el loguin")


def click_sing_in():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordBotonEnglish.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEnglish2.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEspanol.png"], description="botón de iniciar sesión", fallback_coords="1332 x 860")


def click_remember_me():
    return click_image_multiple(["app/ultrabot/images/loginPassword/logoutEspanol.png", "app/ultrabot/images/loginPassword/logoutEnglish.png"], description="botón de iniciar sesión", fallback_coords="1366 x 744")


def click_options_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginOptions.png"], description="botón de opcion de olvidar cuenta", fallback_coords="1682 x 662")


def click_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/forgetAccount.png", "app/ultrabot/images/loginPassword/forgetAccountEspanol.png"], description="botón de iniciar sesión", fallback_coords="1566 x 740")


#!###############################################################################################


def click_minimize_window():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/minimizarVentana.png", "app/ultrabot/images/accionesVentana/minimizarVentana2.png"], description="botón de minimizar ventana", fallback_coords="334 x 98")


def click_refresh():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/recargarPestana.png", "app/ultrabot/images/accionesVentana/recargarPestana2.png", "app/ultrabot/images/accionesVentana/recargarPestana3.png"], description="botón de recargar ventana", fallback_coords="1246 x 220")


def click_refresh_location():
    print("Recargando la ubicación...")


def move_mouse_down(pixels=100, duration=0.5):
    try:
        current_x, current_y = pyautogui.position()

        new_y = current_y + pixels

        pyautogui.moveTo(current_x, new_y, duration=duration)
        print(
            f"Mouse movido hacia abajo a la posición ({current_x}, {new_y}).")
    except Exception as e:
        print(f"Error al mover el mouse: {e}")


#! FUNCION PRIINCIPAL


def execute_ultra_bot():
    global last_cookie_id
    print("########################################################################")
    print("INICIANDO EL BOT ULTRA")
    print("########################################################################")
    click_ultra_logo()
    time.sleep(5)



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

        move_mouse_down(pixels=190, duration=0.7)
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

        if close_codigo(espanol=True):
            print("Código de verificación detectado y reiniciando.")
            deslogin()
        else:
            click_minimize_window()
            last_cookie_id += 1
            continue
        time.sleep(3)

        break
