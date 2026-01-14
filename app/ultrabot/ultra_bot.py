import threading
import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id, get_bot_settings, get_ultra_credentials, get_user_agent_by_id, clear_database, fetch_accounts_from_server, save_cookies_to_db, get_repetidas_settings
from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder, kill_ultra_processes
import cv2
import os
import sys
from PIL import ImageGrab
from tkinter import messagebox
from ..code.profile_config import run_checker


pyautogui.FAILSAFE = False
bot_thread = None
bot_repetidas_thread = None


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


#! funcion para loguear


def wait_for_login_interface(max_attempts=3, wait_time=15):
    """
    Espera y verifica que la interfaz de login esté disponible.
    
    Args:
        max_attempts (int): Número máximo de intentos para verificar la interfaz
        wait_time (int): Tiempo de espera entre intentos en segundos
    
    Returns:
        bool: True si la interfaz está disponible, False si no se encuentra después de todos los intentos
    """
    user_input_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/inputEmail.png")
    ]
    
    for attempt in range(max_attempts):
        print(f"🔍 Verificando interfaz de login (intento {attempt + 1}/{max_attempts})...")
        
        for image in user_input_images:
            try:
                if cv2.imread(image) is None:
                    continue
                location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
                if location:
                    print("✅ Interfaz de login detectada correctamente")
                    return True
            except Exception as e:
                print(f"⚠️ Error detectando interfaz de login: {e}")
        
        if attempt < max_attempts - 1:  # No esperar en el último intento
            print(f"⏳ Interfaz de login no detectada. Esperando {wait_time} segundos...")
            time.sleep(wait_time)
    
    print("❌ Interfaz de login no detectada después de todos los intentos")
    return False

def login_with_ultra_credentials():


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

    # 🧹 Limpiar input y pegar usuario con verificación
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    pyperclip.copy(email)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

    # ✅ Verificar 3 veces que el email se pegó correctamente
    email_verified = False
    for attempt in range(3):
        print(f"🔍 Verificando email (intento {attempt + 1}/3)...")
        
        # Seleccionar todo el texto del campo
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        
        # Copiar el contenido actual del campo
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        
        # Obtener el contenido copiado
        current_content = pyperclip.paste().strip()
        
        
        # Verificar si coincide
        if current_content == email:
            print("✅ Email verificado correctamente")
            email_verified = True
            break
        else:
            print(f"❌ Email no coincide en intento {attempt + 1}")
            if attempt < 2:  # No es el último intento
                print("🔄 Reintentando pegar email...")
                # Limpiar y volver a pegar
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("delete")
                pyperclip.copy(email)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)
    
    if not email_verified:
        messagebox.showerror(
            "Error de verificación",
            f"No se pudo verificar que el email se pegó correctamente después de 3 intentos.\n\nEmail esperado: {email}\nÚltimo contenido: {pyperclip.paste()}"
        )
        sys.exit()

    # ⏭️ Ir al campo de contraseña
    pyautogui.press("tab")
    time.sleep(1)  # Aumentar tiempo de espera

    # 🔍 Verificar que el campo de contraseña esté enfocado
    print("🔍 Verificando que el campo de contraseña esté enfocado...")
    
    # Intentar hacer clic en el campo de contraseña si es necesario
    password_field_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/inputPassword.png")
    ]
    
    password_field_clicked = False
    for image in password_field_images:
        try:
            if cv2.imread(image) is None:
                continue
            location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
            if location:
                pyautogui.click(location)
                print("✅ Campo de contraseña detectado y clickeado")
                password_field_clicked = True
                time.sleep(0.5)
                break
        except Exception as e:
            print(f"⚠️ Error detectando campo de contraseña: {e}")
    
    if not password_field_clicked:
        print("ℹ️ Campo de contraseña no detectado por imagen, usando navegación por teclado")
    
    # Verificar que el campo esté enfocado
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.2)
    focused_content = pyperclip.paste().strip()
    
    # Si el contenido no está vacío, significa que estamos en el campo correcto
    if focused_content:
        print("✅ Campo de contraseña detectado y enfocado")
    else:
        print("⚠️ Campo de contraseña puede no estar enfocado, continuando...")

    # 🧹 Limpiar input y pegar contraseña con verificación
    print("🔑 Iniciando proceso de pegado de contraseña...")
    
    # Limpiar portapapeles antes de copiar la contraseña
    pyperclip.copy("")
    time.sleep(0.2)
    
    # Limpiar campo de contraseña
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")
    time.sleep(0.3)
    
    # Copiar contraseña al portapapeles
    pyperclip.copy(password)
    time.sleep(0.3)
    
    # Pegar contraseña
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)  # Aumentar tiempo de espera después del pegado

    # ✅ Verificar que el pegado de contraseña fue exitoso (sin comparar contenido por seguridad)
    print("🔍 Verificando que el pegado de contraseña fue exitoso...")
    
    # Verificar que el campo de contraseña tiene contenido (aunque sea asteriscos)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.3)
    
    # Obtener el contenido copiado (será asteriscos por seguridad)
    current_content = pyperclip.paste().strip()
    
    # Verificar que hay contenido en el campo (no está vacío)
    if current_content:
        print("✅ Contraseña pegada correctamente (campo contiene contenido)")
        print(f"   Campo contiene: {'*' * len(current_content)} (asteriscos por seguridad)")
    else:
        print("❌ Campo de contraseña está vacío, reintentando...")
        
        # Reintentar pegar la contraseña
        for attempt in range(2):  # 2 reintentos adicionales
            print(f"🔄 Reintentando pegar contraseña (intento {attempt + 1}/2)...")
            
            # Limpiar y volver a pegar
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")
            time.sleep(0.3)
            pyperclip.copy(password)
            time.sleep(0.3)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1)
            
            # Verificar nuevamente
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.3)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.3)
            current_content = pyperclip.paste().strip()
            
            if current_content:
                print("✅ Contraseña pegada correctamente en reintento")
                break
            else:
                print(f"❌ Reintento {attempt + 1} falló")
        
        # Si después de todos los reintentos sigue vacío, mostrar error
        if not current_content:
            messagebox.showerror(
                "Error de pegado de contraseña",
                "No se pudo pegar la contraseña en el campo correspondiente después de varios intentos.\n\nVerifica que el campo de contraseña esté disponible y accesible."
            )
            sys.exit()

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

    input_image_paths = [
        get_resource_path("app/ultrabot/images/inputArea/inputArea4.png"),
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

    click_x, click_y = 702, 384
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

    # ➡️ Avanzar al siguiente input
    pyautogui.press("tab")
    time.sleep(0.5)

    # 📋 Obtener y pegar el user agent
    user_agent = get_user_agent_by_id(cookie_id_to_use)
    if not user_agent:
        print("🚫 No se encontró un User Agent para esta cookie. Deteniendo...")
        messagebox.showerror("Falta User Agent", f"No se encontró user agent para el ID {cookie_id_to_use}")
        stop_ultra_bot()
        sys.exit("❌ Proceso detenido por falta de user agent.")

    pyperclip.copy(user_agent)
    pyautogui.hotkey("ctrl", "v")

    # ✔️ Click en botón OK (versión anterior comentada)
    # def click_ok_button():
    #     ok_images = [
    #         get_resource_path("app/ultrabot/images/botonOk/botonOk5.png"),
    #         get_resource_path("app/ultrabot/images/botonOk/botonOk4.png"),
    #         get_resource_path("app/ultrabot/images/botonOk/botonOk.png"),
    #         get_resource_path("app/ultrabot/images/botonOk/botonOk2.png"),
    #         get_resource_path("app/ultrabot/images/botonOk/botonOk3.png")
    #     ]
    #     for ok_image in ok_images:
    #         try:
    #             location = pyautogui.locateCenterOnScreen(ok_image, confidence=0.8)
    #             if location:
    #                 pyautogui.click(location)
    #                 return
    #         except Exception as e:
    #             print(f"⚠️ Error detectando {ok_image}: {e}")
    #     print("❌ Botón OK no detectado, usando coordenadas de fallback...")
    #     fallback_x, fallback_y = 1011, 620
    #     pyautogui.click(fallback_x, fallback_y)

    def click_ok_button():
        # Nueva versión: presionar tab 4 veces y luego enter
        pyautogui.press('tab', presses=4)
        pyautogui.press('enter')

    time.sleep(1)
    click_ok_button()
    time.sleep(2)

    try:
        if pyautogui.locateOnScreen(get_resource_path("app/ultrabot/images/ingresarCookie/cookieNoValidaNueva.png"), confidence=0.8):
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
                if pyautogui.locateOnScreen(get_resource_path("app/ultrabot/images/ingresarCookie/cookieNoValidaNueva.png"), confidence=0.8):
                    print("🚫 Cookie sigue siendo inválida. Cancelando...")
                    cancel_x, cancel_y = 923, 622
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
    """Busca imágenes en pantalla y, si encuentra alguna, hace clic en las coordenadas proporcionadas."""
    print(description)

    for image in image_paths:
        if find_image(image, confidence=confidence):
            if fallback_coords:
                try:
                    x, y = map(int, fallback_coords.split(" x "))
                    print(f"✅ Imagen detectada. Haciendo clic en ({x}, {y})")

                    # 🔹 Movimiento instantáneo sin sombras en el trayecto
                    pyautogui.moveTo(x, y)
                    # Asegurar que el mouse llegó antes de hacer clic
                    time.sleep(0.1)

                    # 🔹 Clic sin riesgo de que ocurra antes de tiempo
                    pyautogui.click()

                    return True
                except ValueError:
                    print(
                        f"⚠️ Coordenadas inválidas: '{fallback_coords}'. Ignorando clic.")

    print("❌ No se encontró ninguna imagen. Continuando con el código.")
    return False
# Click a una imagen con doble validacion de varias imagenes


def click_image_with_fallback(image_list, additional_image, description="", primary_coords=None, fallback_coords=None, confidence=0.7):
    print(description)




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

def click_europa_boton():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png",], description="boron de europa", fallback_coords="249 x 197", confidence=0.9)

def click_europa_boton2():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/ventanaGrisEuropa3.png"], description="boton de eutopa espanol", fallback_coords="269 x 218", confidence=0.9)



def click_ultra_logo():
    return click_image_multiple(["app/ultrabot/images/ultraLogo/ultraLogo.png", "app/ultrabot/images/ultraLogo/ultraLogo2.png", "app/ultrabot/images/ultraLogo/ultraLogo3.png", "app/ultrabot/images/ultraLogo/ultraLogo4.png"], description="Logo de ultra", fallback_coords="171 x 749")


def click_add_account():
    return click_image_multiple(["app/ultrabot/images/agregarCuenta/agregarCuenta.png", "app/ultrabot/images/agregarCuenta/agregarCuenta3.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles.png", "app/ultrabot/images/agregarCuenta/agregarCuentaIngles2.png"], description="botón de agregar cuenta", fallback_coords="1243 x 167")


def click_panel_dropDown():
    return click_image_multiple(["app/ultrabot/images/panelDesplegableDown/panelDesplegableDown.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown2.png", "app/ultrabot/images/panelDesplegableDown/panelDesplegableDown3.png"], description="panel desplegable", fallback_coords="585 x 92")


def click_add_cookie():
    return click_image_multiple(["app/ultrabot/images/ingresarCookie/ingresarCookies.png", "app/ultrabot/images/ingresarCookie/ingresarCookies2.png", "app/ultrabot/images/ingresarCookie/ingresarCookies3.png"], description="botón de agregar cookie", fallback_coords="751 x 109")


def click_coordinates(x, y):
    """Hace click en coordenadas específicas"""
    try:
        pyautogui.click(x, y)
        print(f"✅ Click realizado en coordenadas ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error al hacer click en coordenadas ({x}, {y}): {e}")
        return False


def click_ok_button():
    return click_image_multiple(["app/ultrabot/images/botonOk/botonOk4.png", "app/ultrabot/images/botonOk/botonOk.png", "app/ultrabot/images/botonOk/botonOk2.png", "app/ultrabot/images/botonOk/botonOk3.png"], description="botón Ok", fallback_coords="886 x 582")


def click_menu_me():
    return click_image_multiple(["app/ultrabot/images/menuDesplegable/menuDesplegableMe.png", "app/ultrabot/images/menuDesplegable/menuDesplegableMe2.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo.png", "app/ultrabot/images/menuDesplegable/menuDesplegableYo2.png"], description="menú desplegable Me", fallback_coords="978 x 164")


def click_sign_out():
    return click_image_multiple(["app/ultrabot/images/singout/signOut.png", "app/ultrabot/images/singout/signOut2.png", "app/ultrabot/images/singout/signOutEspanol.png", "app/ultrabot/images/singout/signOutEspanol2.png"], description="botón de cerrar sesión", fallback_coords="787 x 573")

# Funcion para sign out pero cuando hay una segunda alternativa y se verifica que la pantalla sea blanca


def click_sign_out_2(coords):




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
    try:
        current_x, current_y = pyautogui.position()
        new_y = current_y + pixels
        pyautogui.moveTo(current_x, new_y, duration=duration)
        print(f"Mouse movido hacia abajo a la posición ({current_x}, {new_y}).")
    except Exception as e:
        print(f"Error al mover el mouse: {e}")


def get_pre_check_images_and_coords():
    return [
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png", "249 x 197"),
        ("app/ultrabot/images/accionesVentana/ventanaGrisEuropa3.png", "269 x 218"),
 
    ]


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
        time.sleep(15)
        # click_europa_boton()
        # time.sleep(1)
        # click_europa_boton2()

        login_with_ultra_credentials()
        time.sleep(8)

        config = get_bot_settings()

        if config:
            MAX_ITERATIONS = config["iterations"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            MAX_ITERATIONS = 16
            TIEMPO_ESPERA = 7200

        iteration_count = 0

        #! Funciona bien

        # 🔄 Proceso de inicialización: limpiar BD y obtener cuentas del servidor
        print("🧹 Limpiando base de datos local...")
        clear_database()
        
        print(f"🌐 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
        accounts = fetch_accounts_from_server(MAX_ITERATIONS)
        
        if not accounts:
            print("❌ No se pudieron obtener cuentas del servidor. Deteniendo el bot.")
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        
        # Guardar las cuentas obtenidas en la base de datos local
        print(f"💾 Guardando {len(accounts)} cuentas en la base de datos local...")
        save_cookies_to_db(accounts)
        print("✅ Cuentas guardadas exitosamente. Iniciando procesamiento...")

        while self.running:
            
            if iteration_count >= MAX_ITERATIONS:
                print("🎯 Límite de iteraciones alcanzado. Ejecutando acciones de pestañas...")
                click_europa_boton()
                time.sleep(1)
                click_europa_boton2()

                time.sleep(2)
                click_start_all_tabs()
                time.sleep(2)
                click_europa_boton()
                time.sleep(1)   
                click_europa_boton2()

                # Primer intento
                if not click_acept_actionTabs():
                    print("🔁 Reintentando click en botón aceptar...")
                    time.sleep(1)
                    click_acept_actionTabs()

                print(f"⏳ Esperando {TIEMPO_ESPERA} segundos antes de continuar...")
                print(f"📊 Dividiendo el tiempo de espera en 4 partes de {TIEMPO_ESPERA // 4} segundos cada una...")
                
                # Dividir el tiempo de espera en 4 partes iguales
                tiempo_por_parte = TIEMPO_ESPERA // 4

                # Primera parte: solo esperar
                print(f"⏱️ Parte 1/4: Esperando {tiempo_por_parte} segundos...")
                time.sleep(tiempo_por_parte)
                print("✅ Parte 1/4 completada.")
                
                # Ciclo para las partes 2, 3 y 4: ejecutar acciones y luego esperar
                for parte in range(3):
                    parte_numero = parte + 2  # 2, 3, 4
                    print(f"🚀 Ejecutando acciones para la parte {parte_numero}/4...")

                    # 🛑 Matar todos los procesos de Ultra antes de cerrar la ventana
                    print("🛑 Matando todos los procesos de Ultra...")
                    processes_killed = kill_ultra_processes(show_confirmation=False)
                    if processes_killed:
                        print("✅ Procesos de Ultra terminados correctamente")
                    else:
                        print("⚠️ Algunos procesos de Ultra no pudieron ser terminados, continuando...")
                    
                    print("🖱️ Cerrando ventana principal...")
                    click_coordinates(1339, 10)
                    time.sleep(3) 

                    click_ultra_logo()
                    time.sleep(15)  

                    click_start_all_tabs() 
                    time.sleep(2)
                    # Primer intento para activar las pestañas
                    if not click_acept_actionTabs():
                        print("🔁 Reintentando click en botón aceptar para activar...")
                        time.sleep(1)
                        click_acept_actionTabs()                
                    
                    print(f"⏱️ Parte {parte_numero}/4: Esperando {tiempo_por_parte} segundos...")
                    time.sleep(tiempo_por_parte)
                    print(f"✅ Parte {parte_numero}/4 completada.")
                

                print(f"✅ Tiempo de espera completo ({TIEMPO_ESPERA} segundos) finalizado.")


                click_europa_boton()
                time.sleep(1)
                click_europa_boton2()
                

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
                
                # 🖱️ Cerrar ventana principal haciendo click en coordenadas específicas
                print("🖱️ Cerrando ventana principal...")
                click_coordinates(1339, 10)
                
                # ⏳ Esperar tiempo adicional para que Ultra se cierre completamente
                print("⏳ Esperando a que Ultra se cierre completamente...")
                time.sleep(5)  # Tiempo adicional para que Ultra se cierre
                
                # 🛑 Detener todos los procesos de Ultra que puedan estar ejecutándose
                print("🛑 Deteniendo todos los procesos de Ultra...")
                processes_killed = kill_ultra_processes(show_confirmation=False)
                
                if not processes_killed:
                    print("⚠️ No se pudieron detener algunos procesos de Ultra, continuando...")
                else:
                    print("✅ Procesos de Ultra detenidos correctamente")
                
                # 🗑️ Eliminar cache de Ultra con verificación (hasta 3 intentos)
                print("🗑️ Eliminando cache de Ultra...")
                cache_deleted = False
                max_cache_attempts = 3
                
                for cache_attempt in range(max_cache_attempts):
                    print(f"🗑️ Intento de eliminación de cache {cache_attempt + 1}/{max_cache_attempts}...")
                    cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                    
                    if cache_deleted:
                        print("✅ Cache eliminada correctamente")
                        break
                    else:
                        print(f"❌ Fallo en intento {cache_attempt + 1}, reintentando...")
                        if cache_attempt < max_cache_attempts - 1:  # No esperar en el último intento
                            print("⏳ Esperando antes del siguiente intento...")
                            time.sleep(5)  # Esperar más tiempo entre intentos
                            # Detener procesos nuevamente antes del siguiente intento
                            print("🛑 Deteniendo procesos de Ultra nuevamente...")
                            kill_ultra_processes(show_confirmation=False)
                
                if not cache_deleted:
                    print("❌ Error crítico: No se pudo eliminar la cache después de 3 intentos")
                    messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                    break
                
                # 🔄 Proceso de reinicio con reintentos
                max_restart_attempts = 3
                login_successful = False
                
                for restart_attempt in range(max_restart_attempts):
                    print(f"🔄 Reiniciando Ultra (intento {restart_attempt + 1}/{max_restart_attempts})...")
                    
                    if click_ultra_logo():
                        time.sleep(15)
                        # 🔐 Esperar a que la interfaz de login esté disponible
                        print("🔐 Esperando a que la interfaz de login esté disponible...")
                        if wait_for_login_interface(max_attempts=3, wait_time=15):
                            print("🔐 Iniciando proceso de login...")
                            login_with_ultra_credentials()
                            time.sleep(2)
                            login_successful = True
                            break  # ✅ Login exitoso, salir del bucle de reintentos
                        else:
                            print(f"❌ No se pudo detectar la interfaz de login después de varios intentos (intento {restart_attempt + 1})")
                            if restart_attempt < max_restart_attempts - 1:  # No cerrar en el último intento
                                print("🔄 Cerrando ventana y reintentando...")
                                # 🖱️ Cerrar ventana nuevamente
                                click_coordinates(1339, 10)
                                time.sleep(5)  # Tiempo adicional para que Ultra se cierre
                                # 🛑 Detener procesos de Ultra nuevamente
                                print("🛑 Deteniendo procesos de Ultra nuevamente...")
                                kill_ultra_processes(show_confirmation=False)
                                # 🗑️ Eliminar cache nuevamente con verificación
                                print("🗑️ Eliminando cache de Ultra nuevamente...")
                                cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                                if not cache_deleted:
                                    print("⚠️ No se pudo eliminar la cache en el reintento, continuando...")
                    else:
                        print(f"❌ No se pudo hacer click en el logo de Ultra (intento {restart_attempt + 1})")
                        if restart_attempt < max_restart_attempts - 1:  # No cerrar en el último intento
                            print("🔄 Cerrando ventana y reintentando...")
                            # 🖱️ Cerrar ventana nuevamente
                            click_coordinates(1339, 10)
                            time.sleep(5)  # Tiempo adicional para que Ultra se cierre
                            # 🛑 Detener procesos de Ultra nuevamente
                            print("🛑 Deteniendo procesos de Ultra nuevamente...")
                            kill_ultra_processes(show_confirmation=False)
                            # 🗑️ Eliminar cache nuevamente con verificación
                            print("🗑️ Eliminando cache de Ultra nuevamente...")
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                            if not cache_deleted:
                                print("⚠️ No se pudo eliminar la cache en el reintento, continuando...")
                
                if not login_successful:
                    print("❌ No se pudo completar el login después de todos los reintentos")
                    messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                    break  # Salir del bucle principal si no se puede hacer login
                
                # 🧹 Limpiar base de datos y obtener nuevas cuentas del servidor
                print("🧹 Limpiando base de datos local...")
                clear_database()
                
                print(f"🌐 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
                accounts = fetch_accounts_from_server(MAX_ITERATIONS)
                
                if not accounts:
                    print("❌ No se pudieron obtener cuentas del servidor. Deteniendo el bot.")
                    messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                    break
                
                # Guardar las cuentas obtenidas en la base de datos local
                print(f"💾 Guardando {len(accounts)} cuentas en la base de datos local...")
                save_cookies_to_db(accounts)
                print("✅ Cuentas guardadas exitosamente. Reiniciando procesamiento...")
                
                iteration_count = 0  # 🔄 Resetear contador para que vuelva a iniciar
                last_cookie_id = 1  # 🔄 Resetear el ID de cookie
                continue  # ⏭️ Reinicia el bucle sin procesar más cookies

            # 🔹 Incrementamos el contador AL INICIO para asegurar que se cuenta correctamente
            iteration_count += 1
            print(f"🔥 Iniciando iteración {iteration_count}/{MAX_ITERATIONS} - Procesando Cookie ID {last_cookie_id}")

            click_add_account()
            time.sleep(10)
            if not self.running:
                break
            
            time.sleep(0.5)
            click_europa_boton()
            time.sleep(0.5)
            click_europa_boton2()
            time.sleep(0.5)
            
            click_add_cookie()
            time.sleep(2)
            if not self.running:
                break

            time.sleep(0.5)
            click_europa_boton()
            time.sleep(0.5)
            click_europa_boton2()
            time.sleep(0.5)
            
            if not find_and_click_input():
                print(f"❌ Cookie con ID {last_cookie_id} inválida o rechazada. Saltando a la siguiente...")
            
                last_cookie_id += 1
                continue
            time.sleep(5)
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


class UltraBotRepetidasThread(threading.Thread):
    """Clase para ejecutar el bot de cuentas repetidas en un hilo separado."""
    
    def __init__(self):
        super().__init__()
        self.running = True  

    def stop(self):
        self.running = False
        
    def run(self):
        global last_cookie_id
        print("########################################################################")
        print("INICIANDO EL BOT ULTRA - CUENTAS REPETIDAS")
        print("########################################################################")

        
        click_ultra_logo()
        time.sleep(15)
        # click_europa_boton()
        # time.sleep(1)
        # click_europa_boton2()

        login_with_ultra_credentials()
        time.sleep(8)



        # 📋 Obtener configuración de repetidas
        config = get_repetidas_settings()

        if config:
            ACCOUNTS_TO_REPEAT = config["accounts_to_repeat"]
            REPETITIONS_COUNT = config["repetitions_count"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            print("⚠️ No se encontró configuración de repetidas. Usando valores por defecto.")
            ACCOUNTS_TO_REPEAT = 5
            REPETITIONS_COUNT = 3
            TIEMPO_ESPERA = 7200  # 2 horas en segundos

        print("📊 Configuración cargada:")
        print(f"   - Cuentas a repetir: {ACCOUNTS_TO_REPEAT}")
        print(f"   - Cantidad de repeticiones por cuenta: {REPETITIONS_COUNT}")
        print(f"   - Tiempo de espera: {TIEMPO_ESPERA} segundos ({TIEMPO_ESPERA // 60} minutos)")

        # 🔄 Proceso de inicialización: limpiar BD y obtener cuentas del servidor
        print("🧹 Limpiando base de datos local...")
        clear_database()
        
        print(f"🌐 Obteniendo {ACCOUNTS_TO_REPEAT} cuentas del servidor...")
        accounts = fetch_accounts_from_server(ACCOUNTS_TO_REPEAT)
        
        if not accounts:
            print("❌ No se pudieron obtener cuentas del servidor. Deteniendo el bot.")
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        
        # Guardar las cuentas obtenidas en la base de datos local
        print(f"💾 Guardando {len(accounts)} cuentas en la base de datos local...")
        save_cookies_to_db(accounts)
        print("✅ Cuentas guardadas exitosamente. Iniciando procesamiento...")

        while self.running:
            # 🔄 Procesar cada cuenta y repetirla la cantidad de veces configurada
            last_cookie_id = 1
            total_accounts = len(accounts)
            
            for account_index in range(total_accounts):
                if not self.running:
                    break
                
                current_cookie_id = account_index + 1
                print(f"\n🔄 Procesando cuenta {current_cookie_id}/{total_accounts} - Cookie ID {current_cookie_id}")
                
                # Repetir esta cuenta la cantidad de veces configurada
                for repetition in range(REPETITIONS_COUNT):
                    if not self.running:
                        break
                    
                    print(f"   🔁 Repetición {repetition + 1}/{REPETITIONS_COUNT} de la cuenta {current_cookie_id}")
                    
                    click_add_account()
                    time.sleep(10)
                    if not self.running:
                        break
                    
                    time.sleep(0.5)
                    click_europa_boton()
                    time.sleep(0.5)
                    click_europa_boton2()
                    time.sleep(0.5)
                    
                    click_add_cookie()
                    time.sleep(2)
                    if not self.running:
                        break

                    time.sleep(0.5)
                    click_europa_boton()
                    time.sleep(0.5)
                    click_europa_boton2()
                    time.sleep(0.5)
                    
                    # Usar el mismo cookie_id para todas las repeticiones de esta cuenta
                    if not find_and_click_input(cookie_id_override=current_cookie_id):
                        print(f"   ❌ Cookie con ID {current_cookie_id} inválida o rechazada en repetición {repetition + 1}.")
                        # Continuar con la siguiente repetición aunque falle
                        continue
                    
                    time.sleep(5)

            # 🎯 Todas las cuentas procesadas, ejecutar acciones de pestañas
            print("\n🎯 Todas las cuentas procesadas. Ejecutando acciones de pestañas...")
            click_europa_boton()
            time.sleep(1)
            click_europa_boton2()

            time.sleep(2)
            click_start_all_tabs()
            time.sleep(2)
            click_europa_boton()
            time.sleep(1)   
            click_europa_boton2()

            # Primer intento
            if not click_acept_actionTabs():
                print("🔁 Reintentando click en botón aceptar...")
                time.sleep(1)
                click_acept_actionTabs()

            print(f"⏳ Esperando {TIEMPO_ESPERA} segundos ({TIEMPO_ESPERA // 60} minutos) antes de continuar...")
            time.sleep(TIEMPO_ESPERA)
            print("✅ Tiempo de espera completo finalizado.")

            # 🛑 Detener todas las pestañas
            click_europa_boton()
            time.sleep(1)
            click_europa_boton2()
            
            click_stop_all_tabs()
            time.sleep(2)

            # Primer intento
            if not click_acept_stop_actionTabs():
                time.sleep(1)
                click_acept_stop_actionTabs()
                time.sleep(2)

            time.sleep(2)
            print("🛑 Cerrando ventanas abiertas...")
            # 🔄 Cerrar ventanas: total de cuentas * repeticiones
            total_windows = ACCOUNTS_TO_REPEAT * REPETITIONS_COUNT
            for _ in range(total_windows):
                click_close_window()
                time.sleep(0.5)

            print("🔄 Proceso finalizado, reiniciando...")
            
            # 🖱️ Cerrar ventana principal
            print("🖱️ Cerrando ventana principal...")
            click_coordinates(1339, 10)
            
            # ⏳ Esperar tiempo adicional para que Ultra se cierre completamente
            print("⏳ Esperando a que Ultra se cierre completamente...")
            time.sleep(5)
            
            # 🛑 Detener todos los procesos de Ultra
            print("🛑 Deteniendo todos los procesos de Ultra...")
            processes_killed = kill_ultra_processes(show_confirmation=False)
            
            if not processes_killed:
                print("⚠️ No se pudieron detener algunos procesos de Ultra, continuando...")
            else:
                print("✅ Procesos de Ultra detenidos correctamente")
            
            # 🗑️ Eliminar cache de Ultra con verificación (hasta 3 intentos)
            print("🗑️ Eliminando cache de Ultra...")
            cache_deleted = False
            max_cache_attempts = 3
            
            for cache_attempt in range(max_cache_attempts):
                print(f"🗑️ Intento de eliminación de cache {cache_attempt + 1}/{max_cache_attempts}...")
                cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                
                if cache_deleted:
                    print("✅ Cache eliminada correctamente")
                    break
                else:
                    print(f"❌ Fallo en intento {cache_attempt + 1}, reintentando...")
                    if cache_attempt < max_cache_attempts - 1:
                        print("⏳ Esperando antes del siguiente intento...")
                        time.sleep(5)
                        print("🛑 Deteniendo procesos de Ultra nuevamente...")
                        kill_ultra_processes(show_confirmation=False)
            
            if not cache_deleted:
                print("❌ Error crítico: No se pudo eliminar la cache después de 3 intentos")
                messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                break
            
            # 🔄 Proceso de reinicio con reintentos
            max_restart_attempts = 3
            login_successful = False
            
            for restart_attempt in range(max_restart_attempts):
                print(f"🔄 Reiniciando Ultra (intento {restart_attempt + 1}/{max_restart_attempts})...")
                
                if click_ultra_logo():
                    time.sleep(15)
                    # 🔐 Esperar a que la interfaz de login esté disponible
                    print("🔐 Esperando a que la interfaz de login esté disponible...")
                    if wait_for_login_interface(max_attempts=3, wait_time=15):
                        print("🔐 Iniciando proceso de login...")
                        login_with_ultra_credentials()
                        time.sleep(2)
                        login_successful = True
                        break  # ✅ Login exitoso, salir del bucle de reintentos
                    else:
                        print(f"❌ No se pudo detectar la interfaz de login después de varios intentos (intento {restart_attempt + 1})")
                        if restart_attempt < max_restart_attempts - 1:  # No cerrar en el último intento
                            print("🔄 Cerrando ventana y reintentando...")
                            # 🖱️ Cerrar ventana nuevamente
                            click_coordinates(1339, 10)
                            time.sleep(5)  # Tiempo adicional para que Ultra se cierre
                            # 🛑 Detener procesos de Ultra nuevamente
                            print("🛑 Deteniendo procesos de Ultra nuevamente...")
                            kill_ultra_processes(show_confirmation=False)
                            # 🗑️ Eliminar cache nuevamente con verificación
                            print("🗑️ Eliminando cache de Ultra nuevamente...")
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                            if not cache_deleted:
                                print("⚠️ No se pudo eliminar la cache en el reintento, continuando...")
                else:
                    print(f"❌ No se pudo hacer click en el logo de Ultra (intento {restart_attempt + 1})")
                    if restart_attempt < max_restart_attempts - 1:  # No cerrar en el último intento
                        print("🔄 Cerrando ventana y reintentando...")
                        # 🖱️ Cerrar ventana nuevamente
                        click_coordinates(1339, 10)
                        time.sleep(5)  # Tiempo adicional para que Ultra se cierre
                        # 🛑 Detener procesos de Ultra nuevamente
                        print("🛑 Deteniendo procesos de Ultra nuevamente...")
                        kill_ultra_processes(show_confirmation=False)
                        # 🗑️ Eliminar cache nuevamente con verificación
                        print("🗑️ Eliminando cache de Ultra nuevamente...")
                        cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                        if not cache_deleted:
                            print("⚠️ No se pudo eliminar la cache en el reintento, continuando...")
            
            if not login_successful:
                print("❌ No se pudo completar el login después de todos los reintentos")
                messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                break  # Salir del bucle principal si no se puede hacer login
            
            # 🧹 Limpiar base de datos y obtener nuevas cuentas del servidor
            print("🧹 Limpiando base de datos local...")
            clear_database()
            
            print(f"🌐 Obteniendo {ACCOUNTS_TO_REPEAT} cuentas del servidor...")
            accounts = fetch_accounts_from_server(ACCOUNTS_TO_REPEAT)
            
            if not accounts:
                print("❌ No se pudieron obtener cuentas del servidor. Deteniendo el bot.")
                messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                break
            
            # Guardar las cuentas obtenidas en la base de datos local
            print(f"💾 Guardando {len(accounts)} cuentas en la base de datos local...")
            save_cookies_to_db(accounts)
            print("✅ Cuentas guardadas exitosamente. Reiniciando procesamiento...")
            
            # 🔄 El bucle while se reiniciará automáticamente para procesar las nuevas cuentas
            print("\n🔄 Reiniciando ciclo para procesar nuevas cuentas...\n")


def execute_ultra_bot_repetidas():
    """Inicia el bot de cuentas repetidas en un hilo separado."""
    global bot_repetidas_thread

    if bot_repetidas_thread and bot_repetidas_thread.is_alive():
        print("⚠️ El bot de cuentas repetidas ya está en ejecución.")
        return

    bot_repetidas_thread = UltraBotRepetidasThread()
    bot_repetidas_thread.start()


def stop_ultra_bot_repetidas():
    """Detiene el bot de cuentas repetidas sin hacer join en el mismo hilo."""
    global bot_repetidas_thread
    if bot_repetidas_thread and bot_repetidas_thread.is_alive():
        print("🚫 Deteniendo bot de cuentas repetidas...")
        bot_repetidas_thread.stop()  # Solo marca self.running = False
        bot_repetidas_thread = None  # Elimina la referencia al hilo sin hacer join

