import threading
import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id, get_bot_settings, get_ultra_credentials
import cv2
import os
import sys
from PIL import ImageGrab
from tkinter import messagebox
from ..code.profile_config import run_checker


pyautogui.FAILSAFE = False
bot_thread = None


last_cookie_id = 1
last_cookie_text = None

# Funcion para obtener el path dinamico de los archivos


def get_resource_path(relative_path):

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Funcion para arreglas la imagen antes de buscarla


def find_image(image_path, confidence=0.7):
    """Busca una imagen en la pantalla y devuelve su ubicación si la encuentra."""
    image_path = get_resource_path(image_path)
    try:
        if not os.path.exists(image_path):
            print(f"⚠️ La imagen no existe: {image_path}")
            return None

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

def image_exists(image_path, confidence=0.7):
    location = find_image(image_path, confidence)
    return location is not None

def pre_check_and_click(image_coord_pairs, confidence=0.8):
 
    for image_path, coord_string in image_coord_pairs:
        if image_exists(image_path, confidence=confidence):
            try:
                x, y = map(int, coord_string.split(" x "))
                print(f"🟡 Imagen previa detectada ({image_path}). Clic en ({x}, {y})")
                pyautogui.moveTo(x, y)
                time.sleep(0.1)
                pyautogui.click()
                time.sleep(1)
                break  # Solo hace clic en la primera coincidencia
            except ValueError:
                print(f"⚠️ Coordenadas inválidas: '{coord_string}'")
            break



#! funcion para loguear


def login_with_ultra_credentials():
    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    # 🧩 Flujo normal de login
    credentials = get_ultra_credentials()
    if not credentials:
        messagebox.showerror(
            "Credenciales faltantes",
            "Debes ingresar tu email y contraseña de Ultra.\n\nHazlo desde la interfaz de configuración y vuelve a ejecutar la aplicación."
        )
        sys.exit()

    email = credentials["email"]
    password = credentials["password"]

    user_input_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/inputEmail.png")
    ]

    found_user_input = False
    for image in user_input_images:
        try:
            if cv2.imread(image) is None:
                continue
            location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
            if location:
                pyautogui.click(location)
                found_user_input = True
                break
        except Exception as e:
            print(f"⚠️ Error detectando campo usuario: {e}")

    if not found_user_input:
        print("ℹ️ Campo de usuario no detectado. Asumimos que ya estás logueado.")
        return True

    # 🧹 Limpiar input y pegar usuario
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    pyperclip.copy(email)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

    # ⏭️ Ir al campo de contraseña
    pyautogui.press("tab")
    time.sleep(0.5)

    # 🧹 Limpiar input y pegar contraseña
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    pyperclip.copy(password)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

    # 🔒 Clic en botón login
    login_button_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/loginBoton.png")
    ]

    found_login_btn = False
    for image in login_button_images:
        try:
            location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
            if location:
                pyautogui.click(location)
                found_login_btn = True
                break
        except Exception as e:
            print(f"⚠️ Error detectando botón login: {e}")

    if not found_login_btn:
        fallback_x_login, fallback_y_login = 1150, 378
        pyautogui.click(fallback_x_login, fallback_y_login)

    # ✅ Verificar si aparece alguna imagen de error
    time.sleep(2)

    error_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/errorLogin.png"),
        get_resource_path("app/ultrabot/images/accionesVentana/mailInvalido.png")
    ]

    for error_img in error_images:
        try:
            if pyautogui.locateOnScreen(error_img, confidence=0.8):
                messagebox.showerror(
                    "Credenciales incorrectas",
                    "El email o la contraseña ingresados de Ultra son incorrectos.\n\nCorrígelos desde la configuración y vuelve a ejecutar el programa."
                )
                sys.exit()
        except pyautogui.ImageNotFoundException:
            print(f"❌ Imagen no encontrada: {error_img}")
            continue

    return True

# Funcion para buscar el input de la imagen y darle click


def find_and_click_password():
    global last_cookie_id

    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    print("🔍 Buscando campo de contraseña...")

    password_images = [
        "app/ultrabot/images/loginPassword/loginPasswordInput.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish2.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish3.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish4.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputEnglish.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputConFocusEspanol2.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputConFocusEspanol3.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocus.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocusEnglish.png",
        "app/ultrabot/images/loginPassword/loginPasswordInputSinFocusEspanol2.png"
    ]

    if any(find_image(image) for image in password_images):
        click_x, click_y = 634, 342
        print(f"🖱️ Haciendo clic en ({click_x}, {click_y})")
        pyautogui.moveTo(click_x, click_y)
        time.sleep(0.1)
        pyautogui.click()

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")

        password = get_password_by_id(last_cookie_id)
        if password:
            pyperclip.copy(password)
            print("########################################################")
            print(f"🔑 Contraseña con ID {last_cookie_id} copiada al portapapeles.")
            print("########################################################")
            pyautogui.hotkey("ctrl", "v")
            return True

    print("❌ No se encontró el campo de contraseña en pantalla.")
    return False

# Funcion para encontrar el input de la cookie


def find_and_click_input(cookie_id_override=None):
    global last_cookie_id, last_cookie_text

    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    input_image_paths = [
        get_resource_path("app/ultrabot/images/inputArea/inputArea.png"),
        get_resource_path("app/ultrabot/images/inputArea/inputArea2.png"),
        get_resource_path("app/ultrabot/images/inputArea/inputArea3.png")
    ]

    found = False
    for image in input_image_paths:
        try:
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
        print("❌ No se encontró ninguna imagen de input. Continuando...")

    click_x, click_y = 692, 392
    print(f"🖱️ Clic en ({click_x}, {click_y})")
    pyautogui.click(click_x, click_y)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")

    cookie_id_to_use = cookie_id_override if cookie_id_override is not None else last_cookie_id
    cookie_text = get_cookie_by_id(cookie_id_to_use)

    if not cookie_text:
        print("🚫 No se encontraron más cookies. Deteniendo Ultra Bot.")
        messagebox.showinfo("Ejecución finalizada", "Bot detenido por falta de cookies.")
        stop_ultra_bot()
        sys.exit("❌ Proceso detenido por falta de cookies.")

    print(f"🍪 Cookie ID {cookie_id_to_use} procesada.")
    last_cookie_text = cookie_text
    pyperclip.copy(cookie_text)
    pyautogui.hotkey("ctrl", "v")

    def click_ok_button():
        ok_images = [
            get_resource_path("app/ultrabot/images/botonOk/botonOk.png"),
            get_resource_path("app/ultrabot/images/botonOk/botonOk2.png"),
            get_resource_path("app/ultrabot/images/botonOk/botonOk3.png")
        ]
        for ok_image in ok_images:
            try:
                location = pyautogui.locateCenterOnScreen(ok_image, confidence=0.8)
                if location:
                    pyautogui.click(location)
                    return
            except Exception as e:
                print(f"⚠️ Error detectando {ok_image}: {e}")
        print("❌ Botón OK no detectado, usando coordenadas de fallback...")
        fallback_x, fallback_y = 910, 543
        pyautogui.click(fallback_x, fallback_y)

    time.sleep(1)
    click_ok_button()
    time.sleep(2)

    try:
        if pyautogui.locateOnScreen(get_resource_path("app/ultrabot/images/ingresarCookie/cookieNoValida.png"), confidence=0.8):
            print("⚠️ Cookie no válida detectada. Reintentando...")
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")
            pyperclip.copy(cookie_text)
            pyautogui.hotkey("ctrl", "v")
            click_ok_button()
            time.sleep(2)

            try:
                if pyautogui.locateOnScreen(get_resource_path("app/ultrabot/images/ingresarCookie/cookieNoValida.png"), confidence=0.8):
                    print("🚫 Cookie sigue siendo inválida. Cancelando...")
                    cancel_x, cancel_y = 1000, 543
                    pyautogui.click(cancel_x, cancel_y)
                    return
            except pyautogui.ImageNotFoundException:
                print("✅ Cookie válida en segundo intento.")
                pass

    except pyautogui.ImageNotFoundException:
        print("✅ Cookie válida, no se encontró aviso de error.")

    return True

#! Verificacion de codigo

# Buscar cuando hay un código de verificación
def close_codigo(espanol=False):
    print(f"🔍 Buscando código de verificación {'en español' if espanol else ''}...")

    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    images = [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion.png",
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion2.png"
    ] if not espanol else [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacionEspanol.png"
    ]

    if any(find_image(image) for image in images):
        print("🚀 Código de verificación detectado. Iniciando proceso de verificación...")
        run_checker()

        time.sleep(2)  # Esperar un poco tras cerrar Chrome

        # Buscar input del código
        if find_image("app/ultrabot/images/accionesVentana/enterCode.png"):
            print("📌 Campo para ingresar código encontrado.")
        else:
            print("⚠️ No se encontró el campo para ingresar el código, pero se intentará pegar el código igualmente.")

        pyautogui.click(386, 320)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')

        time.sleep(1)

        # Buscar botón de submit
        if find_image("app/ultrabot/images/accionesVentana/submitBoton.png"):
            print("✅ Botón de submit encontrado.")
        else:
            print("⚠️ No se encontró el botón de submit, pero se intentará hacer clic igualmente.")

        pyautogui.click(396, 397)

        return True

    print("❌ No se encontró ninguna imagen de código de verificación.")
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

# Click a una imagen, pero con varias opciones


def click_image_multiple(image_paths, description="", fallback_coords=None, confidence=0.7):
    """Busca imágenes en pantalla y, si encuentra alguna, hace clic en las coordenadas proporcionadas.
    Antes de eso, verifica si existe una imagen específica (por ejemplo, una advertencia) y hace clic en un lugar fijo si aparece."""

    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    # 🧭 Búsqueda normal de imágenes
    print(description)

    for image in image_paths:
        if find_image(image, confidence=confidence):
            if fallback_coords:
                try:
                    x, y = map(int, fallback_coords.split(" x "))
                    print(f"✅ Imagen detectada. Haciendo clic en ({x}, {y})")

                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.click()

                    return True
                except ValueError:
                    print(f"⚠️ Coordenadas inválidas: '{fallback_coords}'. Ignorando clic.")

    print("❌ No se encontró ninguna imagen. Continuando con el código.")
    return False

# Click a una imagen con doble validacion de varias imagenes


def click_image_with_fallback(image_list, additional_image, description="", primary_coords=None, fallback_coords=None, confidence=0.7):
    print(description)
    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    # 🔍 Verificación principal
    list_image_found = any(find_image(image, confidence=confidence) for image in image_list)
    additional_image_found = find_image(additional_image, confidence=confidence)

    if list_image_found and additional_image_found:
        print("✅ Ambas imágenes detectadas.")
        if primary_coords:
            try:
                x, y = map(int, primary_coords.split(" x "))
                print(f"🖱️ Haciendo clic en ({x}, {y}) por coincidencia doble.")
                pyautogui.moveTo(x, y)
                time.sleep(0.1)
                pyautogui.click()
                return True
            except ValueError:
                print(f"⚠️ Coordenadas inválidas: '{primary_coords}'. No se hizo clic.")

    elif list_image_found:
        print("✅ Imagen de la lista detectada (sin imagen adicional).")
        if fallback_coords:
            try:
                x, y = map(int, fallback_coords.split(" x "))
                print(f"🖱️ Haciendo clic en ({x}, {y}) por coincidencia simple.")
                pyautogui.moveTo(x, y)
                time.sleep(0.1)
                pyautogui.click()
                return True
            except ValueError:
                print(f"⚠️ Coordenadas inválidas: '{fallback_coords}'. No se hizo clic.")

    else:
        print("❌ No se encontró ninguna imagen de la lista. No se hizo clic.")

    return False

#! Funciones específicas para cada acción


def click_ultra_logo():
    return click_image_multiple(["app/ultrabot/images/ultraLogo/ultraLogo.png", "app/ultrabot/images/ultraLogo/ultraLogo2.png", "app/ultrabot/images/ultraLogo/ultraLogo3.png", "app/ultrabot/images/ultraLogo/ultraLogo4.png"], description="Logo de ultra", fallback_coords="171 x 749")


def click_add_account():
    return click_image_multiple(["app/ultrabot/images/agregarCuenta/agregarCuenta.png", "app/ultrabot/images/agregarCuenta/agregarCuenta3.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles2.png"], description="botón de agregar cuenta", fallback_coords="1243 x 167")


def click_panel_dropDown():
    return click_image_multiple(["app/ultrabot/images/panelDesplegableDown/panelDesplegableDown.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown2.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown3.png"], description="panel desplegable", fallback_coords="585 x 92")


def click_add_cookie():
    return click_image_multiple(["app/ultrabot/images/ingresarCookie/ingresarCookies.png", "app/ultrabot/images/ingresarCookie/ingresarCookies2.png", "app/ultrabot/images/ingresarCookie/ingresarCookies3.png"], description="botón de agregar cookie", fallback_coords="751 x 109")


def click_ok_button():
    return click_image_multiple(["app/ultrabot/images/botonOk/botonOk.png", "app/ultrabot/images/botonOk/botonOk2.png", "app/ultrabot/images/botonOk/botonOk3.png"], description="botón Ok", fallback_coords="1082 x 451")


def click_menu_me():
    return click_image_multiple(["app/ultrabot/images/menuDesplegable/menuDesplegableMe.png", "app/ultrabot/images/menuDesplegable/menuDesplegableMe2.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo2.png"], description="menú desplegable Me", fallback_coords="978 x 164")


def click_sign_out():
    return click_image_multiple(["app/ultrabot/images/singout/signOut.png", "app/ultrabot/images/singout/signOut2.png", "app/ultrabot/images/singout/signOutEspanol.png", "app/ultrabot/images/singout/signOutEspanol2.png"], description="botón de cerrar sesión", fallback_coords="787 x 573")

# Funcion para sign out pero cuando hay una segunda alternativa y se verifica que la pantalla sea blanca


def click_sign_out_2(coords):
    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    # 🔍 Procedimiento normal
    try:
        x, y = map(int, coords.split(" x "))
        pixel_color = ImageGrab.grab().getpixel((x, y))

        if pixel_color[:3] == (255, 255, 255):
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            print(f"✅ Clic en ({x}, {y}) - Color: {pixel_color}")
            return True
        else:
            print(f"❌ No se hizo clic en ({x}, {y}) - Color: {pixel_color}")
            return False

    except ValueError:
        print(f"⚠️ Coordenadas inválidas: '{coords}'")
        return False




def click_location():
    return click_image_multiple(["app/ultrabot/images/location/locationImage.png", "app/ultrabot/images/location/locationImageEspanol.png"], description="Pantalla de location", fallback_coords="702 x 108")
#!###############################################################################################
#! SECUENCIA NUEVA


def click_login_whit_email():
    images_to_validate = [
        "app/ultrabot/images/loginPassword/loginPasswordEnglish4.png",
        "app/ultrabot/images/loginPassword/loginPasswordEnglish3.png",
        "app/ultrabot/images/loginPassword/loginPasswordEnglish.png",
        "app/ultrabot/images/loginPassword/loginPasswordEnglish2.png",
        "app/ultrabot/images/loginPassword/loginPasswordEspanol.png",
        "app/ultrabot/images/loginPassword/loginPasswordEspanol2.png"
    ]

    additional_image = "app/ultrabot/images/loginPassword/loginPasswordEnglishIncomplete3.png"

    return click_image_with_fallback(
        images_to_validate,
        additional_image,
        description="Verificando botones de inicio de sesión con doble validación",
        primary_coords="302 x 479",    # Clic si ambas imágenes están presentes
        fallback_coords="302 x 409",   # Clic si solo la imagen de la lista está presente
        confidence=0.9
    )


def click_login_whit_email_incomplete():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordEnglishIncomplete2.png", "app/ultrabot/images/loginPassword/loginPasswordEnglishIncomplete1.png"], description="Botón incompleto de iniciar sesión con Email", fallback_coords="302 x 409", confidence=0.9)


def click_close_boton():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginExit2.png", "app/ultrabot/images/loginPassword/loginExit.png"], description="botón de X de detener el loguin", fallback_coords="836 x 429")


def click_sing_in():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginPasswordBotonEnglish.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEnglish2.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEspanol2.png", "app/ultrabot/images/loginPassword/loginPasswordBotonEspanol.png"], description="botón de iniciar sesión", fallback_coords="659 x 448")


def click_remember_me():
    return click_image_multiple(["app/ultrabot/images/loginPassword/logoutEspanol.png", "app/ultrabot/images/loginPassword/logoutEspanol2.png", "app/ultrabot/images/loginPassword/logoutEnglish.png"], description="botón de remember me", fallback_coords="680 x 370")


def click_options_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/loginOptions2.png", "app/ultrabot/images/loginPassword/loginOptions.png"], description="botón de opcion de olvidar cuenta", fallback_coords="842 x 329")


def click_forget_account():
    return click_image_multiple(["app/ultrabot/images/loginPassword/forgetAccount2.png", "app/ultrabot/images/loginPassword/forgetAccount.png", "app/ultrabot/images/loginPassword/forgetAccountEspanol.png", "app/ultrabot/images/loginPassword/forgetAccountEspanol2.png"], description="botón de iniciar sesión", fallback_coords="773 x 371")


#!###############################################################################################


def click_minimize_window():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/minimizarVentana.png", "app/ultrabot/images/accionesVentana/minimizarVentana2.png"], description="botón de minimizar ventana", fallback_coords="166 x 45")


def click_close_window():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/cerrarVentana.png"], description="botón de cerrar ventana", fallback_coords="183 x 45")


def click_refresh():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/recargarPestana.png", "app/ultrabot/images/accionesVentana/recargarPestana2.png", "app/ultrabot/images/accionesVentana/recargarPestana3.png"], description="botón de recargar ventana", fallback_coords="702 x 108")

# Nuevo proceso automatico


def click_start_all_tabs():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/activaDesactivaPestanas.png"], description="botón de iniciar todas las tabs", fallback_coords="1290 x 100")


def click_stop_all_tabs():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/activaDesactivaPestanas.png"], description="botón de recargar ventana", fallback_coords="1179 x 100")


def click_acept_actionTabs():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/aceptaActivaDesactivaPestana.png"], description="boton para aceptar arrancar las tabs o detenerlas", fallback_coords="976 x 445")

def click_acept_stop_actionTabs():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/aceptarStopTabs.png"], description="boton para aceptar o detenerlas", fallback_coords="974 x 212")


def move_mouse_down(pixels=100, duration=0.5):
    pre_check_images_and_coords = [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "256 x 195"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa2.png", "272 x 234") 
    ]

    pre_check_and_click(pre_check_images_and_coords)



    try:
        current_x, current_y = pyautogui.position()
        new_y = current_y + pixels
        pyautogui.moveTo(current_x, new_y, duration=duration)
        print(f"Mouse movido hacia abajo a la posición ({current_x}, {new_y}).")
    except Exception as e:
        print(f"Error al mover el mouse: {e}")



#! FUNCION PRIINCIPAL


class UltraBotThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.running = True  

    def stop(self):
        self.running = False

    def run(self):
        global last_cookie_id
        print("########################################################################")
        print("INICIANDO EL BOT ULTRA")
        print("########################################################################")

        click_ultra_logo()
        time.sleep(10)

        login_with_ultra_credentials()
        time.sleep(4)

        config = get_bot_settings()

        if config:
            MAX_ITERATIONS = config["iterations"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            MAX_ITERATIONS = 16
            TIEMPO_ESPERA = 7200

        iteration_count = 0

        #! Funciona bien
        def deslogin():
            print("Ejecutando función cuando se desloguea la cuenta")

            if not click_login_whit_email():
                print("✅ Se encontró el botón incompleto de iniciar sesión con Email.")
                return
            time.sleep(1.5)

            find_and_click_password()
            time.sleep(3)

            click_sing_in()
            time.sleep(6)

        #! Funciona bien
        def login_direct():
            print("Ejecutando función de logueo directo")

            # Intentar hacer clic en "Me", si falla, salir de la función
            if not click_menu_me():
                print("❌ No se pudo encontrar el botón 'Me'. Cancelando login_direct().")
                return

            time.sleep(2)

            click_sign_out()
            time.sleep(0.5)
            click_sign_out_2("796 x 599")
            time.sleep(3)

            click_remember_me()
            time.sleep(5)

            click_login_whit_email()
            time.sleep(1.5)

            find_and_click_password()
            time.sleep(3)

            click_sing_in()
            time.sleep(6)

        #! funciona bien
        def request_password():
            print("Ejecutando función para solicitar contraseña")
            if not find_and_click_password():
                print(
                    "No se pudo encontrar el input para solicitar contraseña, saliendo de request_password()")
                return
            time.sleep(3)
            click_sing_in()
            time.sleep(6)

        def login_again():

            click_refresh()

            time.sleep(5)
            click_add_cookie()
            time.sleep(2)

            if not find_and_click_input():
                print(f"❌ Cookie con ID {last_cookie_id} inválida o rechazada. Saltando a la siguiente...")

            time.sleep(2)


            click_refresh()
            time.sleep(2)

            move_mouse_down(pixels=190, duration=0.7)
            time.sleep(15)


            print("Pasaron los 30 segundos. Iniciando variantes")

            if click_location():
                move_mouse_down(pixels=190, duration=0.7)
                time.sleep(8)
                print("✅ Location encontrado, refrescando pantalla")


            login_direct()

            deslogin()

            request_password()


        while self.running:
            if iteration_count >= MAX_ITERATIONS:
                print("🎯 Límite de iteraciones alcanzado. Ejecutando acciones de pestañas...")

                time.sleep(2)
                click_start_all_tabs()
                time.sleep(2)

                # Primer intento
                if not click_acept_actionTabs():
                    print("🔁 Reintentando click en botón aceptar...")
                    time.sleep(1)
                    click_acept_actionTabs()

                print(f"⏳ Esperando {TIEMPO_ESPERA} segundos antes de continuar...")
                time.sleep(TIEMPO_ESPERA)

                click_stop_all_tabs()  # ⏹️ Detener todas las pestañas
                time.sleep(2)

                # Primer intento
                if not click_acept_stop_actionTabs():
                    time.sleep(1)
                    click_acept_stop_actionTabs()
                    # ✅ Confirmar acción
                    time.sleep(2)

                time.sleep(2)
                print("🛑 Cerrando ventanas abiertas...")
                # 🔄 Cerrar ventanas la misma cantidad de veces que iteraciones
                for _ in range(MAX_ITERATIONS):
                    click_close_window()
                    time.sleep(0.5)

                print("🔄 Proceso finalizado, reiniciando el contador de iteraciones...")
                iteration_count = 0  # 🔄 Resetear contador para que vuelva a iniciar
                continue  # ⏭️ Reinicia el bucle sin procesar más cookies

            # 🔹 Incrementamos el contador AL INICIO para asegurar que se cuenta correctamente
            iteration_count += 1
            print(f"🔥 Iniciando iteración {iteration_count}/{MAX_ITERATIONS} - Procesando Cookie ID {last_cookie_id}")

            click_add_account()
            time.sleep(10)
            if not self.running:
                break
            
            click_add_cookie()
            time.sleep(2)
            if not self.running:
                break

            if not find_and_click_input():
                print(f"❌ Cookie con ID {last_cookie_id} inválida o rechazada. Saltando a la siguiente...")
                last_cookie_id += 1
                continue

            time.sleep(2)
            if not self.running:
                break

            click_refresh()
            time.sleep(2)
            if not self.running:
                break

            move_mouse_down(pixels=190, duration=0.7)
            time.sleep(20)
            if not self.running:
                break

            print("Pasaron los 30 segundos. Iniciando variantes")

            if click_location():
                move_mouse_down(pixels=190, duration=0.7)
                time.sleep(8)
                print("✅ Location encontrado, refrescando pantalla")
            if not self.running:
                break

            login_direct()
            if not self.running:
                break

            deslogin()
            if not self.running:
                break

            request_password()
            if not self.running:
                break

            if image_exists("app/ultrabot/images/accionesVentana/appleImage.png"):
                login_again()
            
            time.sleep(5)
            if close_codigo():
                print("✅ Código de verificación detectado")
                time.sleep(2.5)
            else:
                print(f"❌ Cookie ID {last_cookie_id} falló al loguearse.")


            if close_codigo(espanol=True):
                print("✅ Código de verificación detectado y reiniciando.")
                time.sleep(2.5)
            else:
                print(f"❌ Cookie ID {last_cookie_id} falló al loguearse.")


            last_cookie_id += 1



def execute_ultra_bot():
    """Inicia el bot en un hilo separado."""
    global bot_thread

    if bot_thread and bot_thread.is_alive():
        print("⚠️ El bot ya está en ejecución.")
        return

    bot_thread = UltraBotThread()
    bot_thread.start()


def stop_ultra_bot():
    """Detiene el bot sin hacer join en el mismo hilo."""
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        print("🚫 Deteniendo bot...")
        bot_thread.stop()  # Solo marca self.running = False
        bot_thread = None  # Elimina la referencia al hilo sin hacer join

