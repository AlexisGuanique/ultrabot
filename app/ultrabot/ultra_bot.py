import threading
import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id, get_bot_settings, get_ultra_credentials, get_user_agent_by_id, clear_database, fetch_accounts_from_server, save_cookies_to_db, get_repetidas_settings
from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder, kill_ultra_processes
import cv2
import os
import sys
import warnings
from PIL import ImageGrab
from tkinter import messagebox
from ..code.profile_config import run_checker

# Suprimir warnings de OpenCV
warnings.filterwarnings('ignore', category=UserWarning)
cv2.setLogLevel(0)  # Suprimir todos los logs de OpenCV

# Excepción personalizada para errores de login
class LoginError(Exception):
    """Excepción para errores durante el proceso de login."""
    pass


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
            return None

        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, grayscale=True)
        if location:
            return location

    except Exception as e:
        pass
    return None

def image_exists(image_path, confidence=0.7):
    location = find_image(image_path, confidence)
    return location is not None

def wait_for_linkedin_detected(max_attempts=5, wait_time=1, confidence=0.7):
    """
    Espera y verifica que la imagen linkedinDetected.PNG esté presente en la pantalla.
    También verifica que los botones de europa estén visibles para asegurar que la interfaz se haya estabilizado.
    
    Args:
        max_attempts (int): Número máximo de intentos para verificar la imagen
        wait_time (int): Tiempo de espera entre intentos en segundos
        confidence (float): Nivel de confianza para la detección (0.0 a 1.0)
    
    Returns:
        bool: True si la imagen está presente, False si no se encuentra después de todos los intentos
    """
    linkedin_image = "app/ultrabot/images/accionesVentana/linkedinDetected.png"
    europa_boton1 = "app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png"
    europa_boton2 = "app/ultrabot/images/accionesVentana/ventanaGrisEuropa3.png"
    
    for attempt in range(max_attempts):
        # Primero verificar que los botones de europa estén visibles (interfaz estabilizada)
        europa_visible = find_image(europa_boton1, confidence=0.9) or find_image(europa_boton2, confidence=0.9)
        
        if europa_visible:
            # Si los botones de europa están visibles, verificar LinkedIn
            if find_image(linkedin_image, confidence=confidence):
                return True
        else:
            # Si los botones de europa no están visibles, esperar un poco más
            time.sleep(0.5)
        
        if attempt < max_attempts - 1:
            time.sleep(wait_time)
    
    return False

def check_welcome_screen_visible(max_attempts=3, wait_time=0.5, confidence=0.7):
    """
    Verifica si la pantalla de bienvenida (welcomeUltra.PNG) está visible.
    Si está visible, significa que el login no fue exitoso.
    
    Args:
        max_attempts (int): Número máximo de intentos para verificar
        wait_time (int): Tiempo de espera entre intentos en segundos
        confidence (float): Nivel de confianza para la detección (0.0 a 1.0)
    
    Returns:
        bool: True si la pantalla de bienvenida está visible (login falló), False si no
    """
    welcome_image = "app/ultrabot/images/accionesVentana/WelcomeUltra.png"
    
    for attempt in range(max_attempts):
        if find_image(welcome_image, confidence=confidence):
            return True
        
        if attempt < max_attempts - 1:
            time.sleep(wait_time)
    
    return False


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
        for image in user_input_images:
            try:
                # Verificar que el archivo existe antes de intentar leerlo
                if not os.path.exists(image):
                    continue
                if cv2.imread(image) is None:
                    continue
                location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
                if location:
                    return True
            except Exception as e:
                pass
        
        if attempt < max_attempts - 1:
            time.sleep(wait_time)
    return False

def login_with_ultra_credentials():
    """
    Realiza el login con las credenciales de Ultra con verificación y reintentos.
    Verifica que el login fue exitoso comprobando que welcomeUltra.PNG no esté visible.
    Solo muestra un mensaje de error después de 5 intentos fallidos.
    
    Returns:
        bool: True si el login fue exitoso, False si falló después de 5 intentos
    """
    print("🔐 Iniciando proceso de login...")
    # 🧩 Flujo normal de login
    credentials = get_ultra_credentials()
    if not credentials:
        # Solo mostrar error si no hay credenciales (error crítico)
        messagebox.showerror(
            "Credenciales faltantes",
            "Debes ingresar tu email y contraseña de Ultra.\n\nHazlo desde la interfaz de configuración y vuelve a ejecutar la aplicación."
        )
        return False

    email = credentials["email"]
    password = credentials["password"]
    
    # Intentar login hasta 5 veces
    max_attempts = 5
    for login_attempt in range(max_attempts):
        print(f"🔄 Intento de login {login_attempt + 1}/{max_attempts}...")
        try:
            # Realizar el proceso de login
            if not _perform_login_attempt(email, password):
                # Si hay un error crítico, continuar al siguiente intento
                if login_attempt < max_attempts - 1:
                    # Cerrar ventana y reintentar
                    click_coordinates(1339, 10)
                    time.sleep(2)
                    click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                    time.sleep(15)
                    wait_for_login_interface(max_attempts=3, wait_time=15)
                continue
            
            # Esperar un momento después del login para que la pantalla se actualice
            time.sleep(3)
            
            # Verificar si welcomeUltra.PNG está visible (indica que el login falló)
            if not check_welcome_screen_visible(max_attempts=3, wait_time=0.5, confidence=0.7):
                # Login exitoso (welcomeUltra.PNG no está visible)
                print("✅ Login exitoso")
                return True
            
            # Si llegamos aquí, el login falló (welcomeUltra.PNG está visible)
            print(f"❌ Login falló en intento {login_attempt + 1}, reintentando...")
            # Si no es el último intento, cerrar ventana y reintentar
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                time.sleep(15)
                wait_for_login_interface(max_attempts=3, wait_time=15)
        except Exception as e:
            # Si hay una excepción, continuar al siguiente intento
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                time.sleep(15)
                wait_for_login_interface(max_attempts=3, wait_time=15)
            continue
    
    # Si llegamos aquí, todos los intentos fallaron
    print("❌ Login falló después de 5 intentos")
    messagebox.showerror(
        "Error de login",
        "No se pudo completar el login después de 5 intentos.\n\nVerifica tus credenciales y que Ultra esté funcionando correctamente."
    )
    return False

def _perform_login_attempt(email, password):
    """
    Realiza un intento de login con las credenciales proporcionadas.
    
    Returns:
        bool: True si el proceso de login se completó (sin verificar éxito), False si hay error crítico
    """

    user_input_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/inputEmail.png")
    ]

    found_user_input = False
    for image in user_input_images:
        try:
            # Verificar que el archivo existe antes de intentar leerlo
            if not os.path.exists(image):
                continue
            if cv2.imread(image) is None:
                continue
            location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
            if location:
                pyautogui.click(location)
                found_user_input = True
                break
        except Exception as e:
            pass

    if not found_user_input:
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
            email_verified = True
            break
        else:
            if attempt < 2:  # No es el último intento
                # Limpiar y volver a pegar
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("delete")
                pyperclip.copy(email)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)
    
    if not email_verified:
        # No mostrar mensaje, solo retornar False para que se reintente
        return False

    # ⏭️ Ir al campo de contraseña
    pyautogui.press("tab")
    time.sleep(1)  # Aumentar tiempo de espera

    # Intentar hacer clic en el campo de contraseña si es necesario
    password_field_images = [
        get_resource_path("app/ultrabot/images/accionesVentana/inputPassword.png")
    ]
    
    password_field_clicked = False
    for image in password_field_images:
        try:
            # Verificar que el archivo existe antes de intentar leerlo
            if not os.path.exists(image):
                continue
            if cv2.imread(image) is None:
                continue
            location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
            if location:
                pyautogui.click(location)
                password_field_clicked = True
                time.sleep(0.5)
                break
        except Exception as e:
            pass
    
    # Verificar que el campo esté enfocado
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.2)
    focused_content = pyperclip.paste().strip()
    
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
    # Verificar que el campo de contraseña tiene contenido (aunque sea asteriscos)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.3)
    
    # Obtener el contenido copiado (será asteriscos por seguridad)
    current_content = pyperclip.paste().strip()
    
    # Verificar que hay contenido en el campo (no está vacío)
    if not current_content:
        # Reintentar pegar la contraseña
        for attempt in range(2):  # 2 reintentos adicionales
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
                break
        
        # Si después de todos los reintentos sigue vacío, retornar False para reintentar
        if not current_content:
            return False

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
            pass

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
                # No mostrar mensaje, solo retornar False para que se reintente
                return False
        except pyautogui.ImageNotFoundException:
            continue

    return True

# Funcion para buscar el input de la imagen y darle click


def find_and_click_password():
    global last_cookie_id


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
        pyautogui.moveTo(click_x, click_y)
        time.sleep(0.1)
        pyautogui.click()

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")

        password = get_password_by_id(last_cookie_id)
        if password:
            pyperclip.copy(password)
            pyautogui.hotkey("ctrl", "v")
            return True

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
            # Verificar que el archivo existe antes de intentar leerlo
            if not os.path.exists(image):
                continue
            if cv2.imread(image) is None:
                continue

            if pyautogui.locateCenterOnScreen(image, confidence=0.8):
                found = True
                break
        except Exception as e:
            pass

    cookie_id_to_use = cookie_id_override if cookie_id_override is not None else last_cookie_id
    cookie_text = get_cookie_by_id(cookie_id_to_use)

    if not cookie_text:
        messagebox.showinfo("Ejecución finalizada", "Bot detenido por falta de cookies.")
        stop_ultra_bot()
        return False
    last_cookie_text = cookie_text

    # 📋 Obtener el user agent
    user_agent = get_user_agent_by_id(cookie_id_to_use)
    if not user_agent:
        messagebox.showerror("Falta User Agent", f"No se encontró user agent para el ID {cookie_id_to_use}")
        stop_ultra_bot()
        return False

    # ✔️ Función auxiliar para hacer click en botón OK
    def click_ok_button():
        ok_images = [
            get_resource_path("app/ultrabot/images/botonOk/botonOk5.png"),
            get_resource_path("app/ultrabot/images/botonOk/botonOk4.png"),
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
                pass
        fallback_x, fallback_y = 1011, 620
        pyautogui.click(fallback_x, fallback_y)

    # 🔄 Función auxiliar para pegar la cookie y user agent
    def paste_cookie_and_user_agent():
        # 🎯 Asegurar que estamos en el campo de cookie (hacer clic en el campo primero)
        print("⌨️ Enfocando campo de cookie...")
        # Hacer clic en el campo de cookie para asegurar que está enfocado
        # Buscar el campo de input de cookie
        input_image_paths = [
            get_resource_path("app/ultrabot/images/inputArea/inputArea4.png"),
            get_resource_path("app/ultrabot/images/inputArea/inputArea.png"),
            get_resource_path("app/ultrabot/images/inputArea/inputArea2.png"),
            get_resource_path("app/ultrabot/images/inputArea/inputArea3.png")
        ]
        
        cookie_field_clicked = False
        for image in input_image_paths:
            try:
                if not os.path.exists(image):
                    continue
                location = pyautogui.locateCenterOnScreen(image, confidence=0.8)
                if location:
                    # Hacer clic en el campo de cookie para enfocarlo
                    pyautogui.click(location)
                    time.sleep(0.3)
                    cookie_field_clicked = True
                    break
            except Exception as e:
                pass
        
        if not cookie_field_clicked:
            print("⚠️ No se pudo encontrar el campo de cookie, usando Tab...")
            pyautogui.press("tab")
            time.sleep(0.3)
        
        # 🎯 Activar botón que selecciona todo el texto (1 tab + enter)
        print("⌨️ Seleccionando todo el texto del campo cookie...")
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.5)

        # 📋 Pegar cookie
        print("📋 Pegando cookie...")
        pyperclip.copy(cookie_text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)  # Aumentar tiempo para asegurar que se pegó

        # ➡️ Asegurar que salimos del campo de cookie antes de ir al user agent
        print("➡️ Moviendo al campo de user agent...")
        # Después de pegar la cookie, el foco puede seguir en el campo de cookie
        # Hacer Tab para avanzar al siguiente campo (user agent)
        # El primer Tab puede ir al botón "Select all" o a otro elemento, así que hacemos Tab dos veces
        pyautogui.press("tab")
        time.sleep(0.4)
        
        # Verificar si estamos en el campo de user agent haciendo Tab una vez más
        # Si el primer Tab nos llevó al campo de user agent, el segundo Tab nos llevará al botón OK
        # Pero para asegurarnos, hacemos Tab una vez más y luego retrocedemos con Shift+Tab
        pyautogui.press("tab")
        time.sleep(0.4)
        
        # Retroceder con Shift+Tab para volver al campo de user agent
        # Esto asegura que estamos en el campo correcto
        pyautogui.hotkey("shift", "tab")
        time.sleep(0.4)
        
        # Seleccionar todo el texto del campo de user agent antes de pegar
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)

        # 📋 Pegar user agent
        print("📋 Pegando user agent...")
        pyperclip.copy(user_agent)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)  # Aumentar tiempo para asegurar que se pegó

        # ✔️ Click en botón OK
        print("✔️ Haciendo clic en botón OK...")
        click_ok_button()
        time.sleep(2)

    # 🔄 Función auxiliar para verificar si la cookie es inválida (más robusta)
    def check_cookie_invalid(max_checks=3, wait_between_checks=0.3, confidence=0.7):
        """Verifica múltiples veces si la imagen de cookie inválida está presente"""
        cookie_no_valida_path = "app/ultrabot/images/ingresarCookie/cookieNoValidaNueva.png"
        detection_count = 0
        
        for check in range(max_checks):
            if find_image(cookie_no_valida_path, confidence=confidence):
                detection_count += 1
            time.sleep(wait_between_checks)
        
        # Si se detectó al menos 2 veces, consideramos que está presente
        return detection_count >= 2

    # 🔄 Intentar pegar la cookie hasta 5 veces
    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        print(f"🍪 Intento {attempt}/{max_attempts} de pegar cookie...")
        paste_cookie_and_user_agent()

        # Esperar un poco más para que la imagen de error aparezca si hay problema
        time.sleep(1.5)

        # Verificar si la cookie se pegó correctamente (verificación robusta)
        cookie_invalid = check_cookie_invalid(max_checks=4, wait_between_checks=0.4, confidence=0.7)
        
        if cookie_invalid:
            print(f"⚠️ Cookie no válida detectada en intento {attempt}")
            
            if attempt < max_attempts:
                # Cerrar el modal y reintentar
                print("🔄 Cerrando modal y reintentando...")
                # Hacer clic en Cancel de manera más robusta
                try:
                    pyautogui.moveTo(924, 620)
                    time.sleep(0.2)
                    pyautogui.click(924, 620)
                    print("✅ Clic en Cancel ejecutado")
                except Exception as e:
                    print(f"⚠️ Error al hacer clic en Cancel: {e}")
                    # Intentar de nuevo
                    pyautogui.click(924, 620)
                
                time.sleep(1.5)
                
                # Verificar que el modal se cerró antes de abrirlo de nuevo
                time.sleep(0.5)
                
                # Abrir el modal de nuevo
                print("🔓 Abriendo modal de cookie nuevamente...")
                click_add_cookie()
                time.sleep(2.5)
            else:
                # Último intento falló, cerrar modal y retornar False
                print("❌ No se pudo pegar la cookie correctamente después de 5 intentos")
                try:
                    pyautogui.moveTo(924, 620)
                    time.sleep(0.2)
                    pyautogui.click(924, 620)
                    print("✅ Clic en Cancel ejecutado (último intento)")
                except Exception as e:
                    print(f"⚠️ Error al hacer clic en Cancel: {e}")
                    pyautogui.click(924, 620)
                time.sleep(0.5)
                return False
        else:
            # Cookie se pegó correctamente
            print("✅ Cookie pegada correctamente")
            return True

    return False

#! Verificacion de codigo

# Buscar cuando hay un código de verificación
def close_codigo(espanol=False):

    images = [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion.png",
        "app/ultrabot/images/codigoVerificacion/codigoVerificacion2.png"
    ] if not espanol else [
        "app/ultrabot/images/codigoVerificacion/codigoVerificacionEspanol.png"
    ]

    if any(find_image(image) for image in images):
        run_checker()
        time.sleep(2)
        pyautogui.click(386, 320)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.click(396, 397)
        return True

    return False



def click_image(image_path, confidence=0.8, offset_x=0, offset_y=0, description=""):

    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence)
        if location:
            click_x = location[0] + offset_x
            click_y = location[1] + offset_y
            pyautogui.click(click_x, click_y)
            return True
    except Exception as e:
        pass
    return False

# Click a una imagen, pero con varias opciones


def click_image_multiple(image_paths, description="", fallback_coords=None, confidence=0.7):
    """Busca imágenes en pantalla y, si encuentra alguna, hace clic en las coordenadas proporcionadas."""
    for image in image_paths:
        if find_image(image, confidence=confidence):
            if fallback_coords:
                try:
                    x, y = map(int, fallback_coords.split(" x "))
                    pyautogui.moveTo(x, y)
                    time.sleep(0.1)
                    pyautogui.click()
                    return True
                except ValueError:
                    pass

    return False
# Click a una imagen con doble validacion de varias imagenes


def click_image_with_fallback(image_list, additional_image, description="", primary_coords=None, fallback_coords=None, confidence=0.7):
    # 🔍 Verificación principal
    list_image_found = any(find_image(image, confidence=confidence) for image in image_list)
    additional_image_found = find_image(additional_image, confidence=confidence)

    if list_image_found and additional_image_found:
        if primary_coords:
            try:
                x, y = map(int, primary_coords.split(" x "))
                pyautogui.moveTo(x, y)
                time.sleep(0.1)
                pyautogui.click()
                return True
            except ValueError:
                pass

    elif list_image_found:
        if fallback_coords:
            try:
                x, y = map(int, fallback_coords.split(" x "))
                pyautogui.moveTo(x, y)
                time.sleep(0.1)
                pyautogui.click()
                return True
            except ValueError:
                pass

    return False

#! Funciones específicas para cada acción

def click_europa_boton():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png",], description="boron de europa", fallback_coords="249 x 212", confidence=0.9)

def click_europa_boton2():
    return click_image_multiple(["app/ultrabot/images/accionesVentana/ventanaGrisEuropa3.png"], description="boton de eutopa espanol", fallback_coords="269 x 233", confidence=0.9)



def click_ultra_logo(max_attempts=5, delay_between_attempts=2):
    """
    Hace clic en el logo de Ultra con reintentos para asegurar que el clic se ejecute correctamente.
    
    Args:
        max_attempts (int): Número máximo de intentos para hacer el clic
        delay_between_attempts (int): Tiempo de espera entre intentos en segundos
    
    Returns:
        bool: True si el clic fue exitoso, False si falló después de todos los intentos
    """
    image_paths = [
        "app/ultrabot/images/ultraLogo/ultraLogo.png",
        "app/ultrabot/images/ultraLogo/ultraLogo2.png",
        "app/ultrabot/images/ultraLogo/ultraLogo3.png",
        "app/ultrabot/images/ultraLogo/ultraLogo4.png"
    ]
    fallback_coords = "171 x 749"
    
    for attempt in range(max_attempts):
        # Buscar la imagen
        image_found = False
        for image in image_paths:
            if find_image(image, confidence=0.7):
                image_found = True
                break
        
        if image_found or attempt == max_attempts - 1:
            try:
                x, y = map(int, fallback_coords.split(" x "))
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.2)
                
                current_x, current_y = pyautogui.position()
                if abs(current_x - x) > 5 or abs(current_y - y) > 5:
                    if attempt < max_attempts - 1:
                        time.sleep(delay_between_attempts)
                        continue
                
                pyautogui.click()
                time.sleep(0.3)
                return True
                
            except ValueError:
                pass
            except Exception as e:
                pass
        
        if attempt < max_attempts - 1:
            time.sleep(delay_between_attempts)
    
    return False


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
        return True
    except Exception as e:
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
            return True
        else:
            return False

    except ValueError:
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
    except Exception as e:
        pass


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
        self.daemon = True  # Hilo daemon: se detiene cuando el programa principal termina  

    def stop(self):
        self.running = False

    def run(self):
        global last_cookie_id
        time.sleep(3)
        
        if not click_ultra_logo(max_attempts=5, delay_between_attempts=2):
            messagebox.showerror("Error", "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.")
            return
        
        time.sleep(15)
        # click_europa_boton()
        # time.sleep(1)
        # click_europa_boton2()

        # login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
        if not login_with_ultra_credentials():
            return  # El mensaje de error ya fue mostrado por login_with_ultra_credentials()
        
        time.sleep(8)



        config = get_bot_settings()

        if config:
            MAX_ITERATIONS = config["iterations"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            MAX_ITERATIONS = 16
            TIEMPO_ESPERA = 7200

        print(f"⚙️ Configuración: {MAX_ITERATIONS} iteraciones, {TIEMPO_ESPERA}s de espera")
        iteration_count = 0

        #! Funciona bien

        print("🗑️ Limpiando base de datos...")
        clear_database()
        print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
        accounts = fetch_accounts_from_server(MAX_ITERATIONS)
        
        if not accounts:
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        
        print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
        save_cookies_to_db(accounts)

        while self.running:
            
            if iteration_count >= MAX_ITERATIONS:
                print(f"📊 Iteración {iteration_count}/{MAX_ITERATIONS} alcanzada, iniciando proceso de tabs...")
                print("▶️ Iniciando todas las tabs...")
                click_europa_boton()
                time.sleep(1)
                click_europa_boton2()

                time.sleep(2)
                click_start_all_tabs()
                time.sleep(2)
                click_europa_boton()
                time.sleep(1)   
                click_europa_boton2()

                if not click_acept_actionTabs():
                    time.sleep(1)
                    click_acept_actionTabs()

                tiempo_por_parte = TIEMPO_ESPERA // 4
                print(f"⏳ Esperando {tiempo_por_parte}s por parte (total: {TIEMPO_ESPERA}s)...")
                time.sleep(tiempo_por_parte)
                
                # Constantes para el manejo de errores de LinkedIn
                ERROR_LINKEDIN_PATH = "app/ultrabot/images/accionesVentana/ErrorLinkedin.PNG"
                MAX_INTENTOS_ERROR = 10
                COORD_ERROR_CLOSE = (915, 438)
                
                for parte in range(3):
                    print(f"  📍 Parte {parte + 1}/3 del proceso...")
                    kill_ultra_processes(show_confirmation=False)
                    click_coordinates(1339, 10)
                    time.sleep(3) 

                    for intento_error in range(MAX_INTENTOS_ERROR):
                        click_ultra_logo()
                        time.sleep(3)
                        
                        if not find_image(ERROR_LINKEDIN_PATH, confidence=0.7):
                            break
                        
                        click_coordinates(*COORD_ERROR_CLOSE)
                        time.sleep(1)
                    
                    time.sleep(15)  

                    click_start_all_tabs() 
                    time.sleep(2)
                    if not click_acept_actionTabs():
                        time.sleep(1)
                        click_acept_actionTabs()                
                    
                    time.sleep(tiempo_por_parte)


                click_europa_boton()
                time.sleep(1)
                click_europa_boton2()
                

                print("⏹️ Deteniendo todas las tabs...")
                click_stop_all_tabs()  # ⏹️ Detener todas las pestañas
                time.sleep(2)

                if not click_acept_stop_actionTabs():
                    time.sleep(1)
                    click_acept_stop_actionTabs()
                    time.sleep(2)

                print(f"🗑️ Cerrando {MAX_ITERATIONS} ventanas...")
                time.sleep(2)
                for _ in range(MAX_ITERATIONS):
                    click_close_window()
                    time.sleep(0.5)

                click_coordinates(1339, 10)
                time.sleep(5)
                
                print("🔪 Eliminando procesos de Ultra...")
                processes_killed = kill_ultra_processes(show_confirmation=False)
                
                print("🗑️ Eliminando cache de Ultra...")
                cache_deleted = False
                max_cache_attempts = 3
                
                for cache_attempt in range(max_cache_attempts):
                    cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                    
                    if cache_deleted:
                        print("✅ Cache eliminada exitosamente")
                        break
                    else:
                        print(f"⚠️ Intento {cache_attempt + 1}/{max_cache_attempts} de eliminar cache falló")
                        if cache_attempt < max_cache_attempts - 1:
                            time.sleep(5)
                            kill_ultra_processes(show_confirmation=False)
                
                if not cache_deleted:
                    messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                    break
                
                print("🔄 Reintentando login después de limpieza...")
                max_restart_attempts = 3
                login_successful = False
                
                for restart_attempt in range(max_restart_attempts):
                    print(f"  🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                    if click_ultra_logo():
                        time.sleep(15)
                        if wait_for_login_interface(max_attempts=3, wait_time=15):
                            # login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
                            if login_with_ultra_credentials():
                                time.sleep(2)
                                login_successful = True
                                break
                            else:
                                login_successful = False
                            break
                        else:
                            if restart_attempt < max_restart_attempts - 1:
                                click_coordinates(1339, 10)
                                time.sleep(5)
                                kill_ultra_processes(show_confirmation=False)
                                cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                    else:
                        if restart_attempt < max_restart_attempts - 1:
                            click_coordinates(1339, 10)
                            time.sleep(5)
                            kill_ultra_processes(show_confirmation=False)
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                
                if not login_successful:
                    messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                    break
                
                print("🔄 Reiniciando ciclo...")
                clear_database()
                accounts = fetch_accounts_from_server(MAX_ITERATIONS)
                
                if not accounts:
                    messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                    break
                
                print(f"✅ Se obtuvieron {len(accounts)} nuevas cuentas del servidor")
                save_cookies_to_db(accounts)
                
                iteration_count = 0  # 🔄 Resetear contador para que vuelva a iniciar
                last_cookie_id = 1  # 🔄 Resetear el ID de cookie
                continue  # ⏭️ Reinicia el bucle sin procesar más cookies

            iteration_count += 1


            click_add_account()
            time.sleep(10)
            if not self.running:
                break
            
            time.sleep(0.5)
            click_europa_boton()
            time.sleep(0.5)
            click_europa_boton2()
            time.sleep(2)  # Esperar más tiempo para que la interfaz se estabilice
            
            # Validar que linkedinDetected.PNG esté presente antes de agregar cookie
            # La función también verifica que los botones de europa estén visibles
            if not wait_for_linkedin_detected(max_attempts=8, wait_time=1, confidence=0.7):
                print(f"⚠️ LinkedIn no detectado para cookie ID {last_cookie_id}, reintentando desde click_add_account()...")
                # Volver al inicio del bucle para abrir una nueva pestaña e intentar de nuevo con la misma cookie
                continue
            
            print(f"🍪 Procesando cookie ID {last_cookie_id}...")
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
                print(f"❌ Error al procesar cookie ID {last_cookie_id}")
                last_cookie_id += 1
                continue
            print(f"✅ Cookie ID {last_cookie_id} procesada exitosamente")
            time.sleep(5)
            

            last_cookie_id += 1



def execute_ultra_bot():
    """Inicia el bot en un hilo separado."""
    global bot_thread

    if bot_thread and bot_thread.is_alive():
        return

    bot_thread = UltraBotThread()
    bot_thread.start()


def stop_ultra_bot():
    """Detiene el bot y espera a que termine."""
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        bot_thread.stop()
        # Esperar un momento para que el hilo detecte el cambio
        time.sleep(0.5)
        bot_thread = None


class UltraBotRepetidasThread(threading.Thread):
    """Clase para ejecutar el bot de cuentas repetidas en un hilo separado."""
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.daemon = True  # Hilo daemon: se detiene cuando el programa principal termina  

    def stop(self):
        self.running = False
        
    def run(self):
        global last_cookie_id
        print("🚀 Iniciando UltraBot Repetidas...")
        time.sleep(3)
        
        print("🖱️ Buscando logo de Ultra...")
        if not click_ultra_logo(max_attempts=5, delay_between_attempts=2):
            messagebox.showerror("Error", "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.")
            return
        
        print("⏳ Esperando carga de Ultra...")
        time.sleep(15)
        # click_europa_boton()
        # time.sleep(1)
        # click_europa_boton2()

        # login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
        if not login_with_ultra_credentials():
            return  # El mensaje de error ya fue mostrado por login_with_ultra_credentials()
        
        time.sleep(8)



        # 📋 Obtener configuración de repetidas
        config = get_repetidas_settings()

        if config:
            ACCOUNTS_TO_REPEAT = config["accounts_to_repeat"]
            REPETITIONS_COUNT = config["repetitions_count"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            ACCOUNTS_TO_REPEAT = 5
            REPETITIONS_COUNT = 3
            TIEMPO_ESPERA = 7200

        print(f"⚙️ Configuración Repetidas: {ACCOUNTS_TO_REPEAT} cuentas, {REPETITIONS_COUNT} repeticiones, {TIEMPO_ESPERA}s de espera")
        print("🗑️ Limpiando base de datos...")
        clear_database()
        print(f"📡 Obteniendo {ACCOUNTS_TO_REPEAT} cuentas del servidor...")
        accounts = fetch_accounts_from_server(ACCOUNTS_TO_REPEAT)
        
        if not accounts:
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        
        print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
        save_cookies_to_db(accounts)

        while self.running:
            # 🔄 Procesar cada cuenta y repetirla la cantidad de veces configurada
            last_cookie_id = 1
            total_accounts = len(accounts)
            print(f"🔄 Procesando {total_accounts} cuentas con {REPETITIONS_COUNT} repeticiones cada una...")
            
            for account_index in range(total_accounts):
                if not self.running:
                    break
                
                current_cookie_id = account_index + 1
                print(f"📋 Procesando cuenta {current_cookie_id}/{total_accounts}...")
                
                for repetition in range(REPETITIONS_COUNT):
                    if not self.running:
                        break
                    
                    print(f"  🔁 Repetición {repetition + 1}/{REPETITIONS_COUNT} de cuenta {current_cookie_id}...")
                    click_add_account()
                    time.sleep(10)
                    if not self.running:
                        break
                    
                    time.sleep(0.5)
                    click_europa_boton()
                    time.sleep(0.5)
                    click_europa_boton2()
                    time.sleep(2)  # Esperar más tiempo para que la interfaz se estabilice
                    
                    # Validar que linkedinDetected.PNG esté presente antes de agregar cookie
                    # La función también verifica que los botones de europa estén visibles
                    if not wait_for_linkedin_detected(max_attempts=8, wait_time=1, confidence=0.7):
                        print(f"  ⚠️ LinkedIn no detectado para cuenta {current_cookie_id}, repetición {repetition + 1}, reintentando desde click_add_account()...")
                        # Volver al inicio del bucle para abrir una nueva pestaña e intentar de nuevo con la misma cookie
                        continue
                    
                    print(f"  🍪 Agregando cookie para cuenta {current_cookie_id}, repetición {repetition + 1}...")
                    click_add_cookie()
                    time.sleep(2)
                    if not self.running:
                        break

                    time.sleep(0.5)
                    click_europa_boton()
                    time.sleep(0.5)
                    click_europa_boton2()
                    time.sleep(0.5)
                    
                    if not find_and_click_input(cookie_id_override=current_cookie_id):
                        print(f"  ❌ Error al procesar cookie para cuenta {current_cookie_id}, repetición {repetition + 1}")
                        continue
                    
                    print(f"  ✅ Cookie procesada exitosamente para cuenta {current_cookie_id}, repetición {repetition + 1}")
                    time.sleep(5)

            click_europa_boton()
            time.sleep(1)
            click_europa_boton2()

            print(f"▶️ Iniciando todas las tabs y esperando {TIEMPO_ESPERA}s...")
            time.sleep(2)
            click_start_all_tabs()
            time.sleep(2)
            click_europa_boton()
            time.sleep(1)   
            click_europa_boton2()

            if not click_acept_actionTabs():
                time.sleep(1)
                click_acept_actionTabs()

            time.sleep(TIEMPO_ESPERA)
            print("⏹️ Tiempo de espera completado, deteniendo tabs...")

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
            total_windows = ACCOUNTS_TO_REPEAT * REPETITIONS_COUNT
            print(f"🗑️ Cerrando {total_windows} ventanas...")
            for _ in range(total_windows):
                click_close_window()
                time.sleep(0.5)

            click_coordinates(1339, 10)
            time.sleep(5)
            
            print("🔪 Eliminando procesos de Ultra...")
            processes_killed = kill_ultra_processes(show_confirmation=False)
            
            print("🗑️ Eliminando cache de Ultra...")
            cache_deleted = False
            max_cache_attempts = 3
            
            for cache_attempt in range(max_cache_attempts):
                cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                
                if cache_deleted:
                    print("✅ Cache eliminada exitosamente")
                    break
                else:
                    print(f"⚠️ Intento {cache_attempt + 1}/{max_cache_attempts} de eliminar cache falló")
                    if cache_attempt < max_cache_attempts - 1:
                        time.sleep(5)
                        kill_ultra_processes(show_confirmation=False)
            
            if not cache_deleted:
                messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                break
            
            print("🔄 Reintentando login después de limpieza...")
            max_restart_attempts = 3
            login_successful = False
            
            for restart_attempt in range(max_restart_attempts):
                print(f"  🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                if click_ultra_logo():
                    time.sleep(15)
                    if wait_for_login_interface(max_attempts=3, wait_time=15):
                        # login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
                        if login_with_ultra_credentials():
                            time.sleep(2)
                            login_successful = True
                            break
                        else:
                            login_successful = False
                        break
                    else:
                        if restart_attempt < max_restart_attempts - 1:
                            click_coordinates(1339, 10)
                            time.sleep(5)
                            kill_ultra_processes(show_confirmation=False)
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                else:
                    if restart_attempt < max_restart_attempts - 1:
                        click_coordinates(1339, 10)
                        time.sleep(5)
                        kill_ultra_processes(show_confirmation=False)
                        cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
            
            if not login_successful:
                messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                break
            
            print("🔄 Reiniciando ciclo de repetidas...")
            clear_database()
            accounts = fetch_accounts_from_server(ACCOUNTS_TO_REPEAT)
            
            if not accounts:
                messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                break
            
            print(f"✅ Se obtuvieron {len(accounts)} nuevas cuentas del servidor")
            save_cookies_to_db(accounts)


def execute_ultra_bot_repetidas():
    """Inicia el bot de cuentas repetidas en un hilo separado."""
    global bot_repetidas_thread

    if bot_repetidas_thread and bot_repetidas_thread.is_alive():
        return

    bot_repetidas_thread = UltraBotRepetidasThread()
    bot_repetidas_thread.start()


def stop_ultra_bot_repetidas():
    """Detiene el bot de cuentas repetidas y espera a que termine."""
    global bot_repetidas_thread
    if bot_repetidas_thread and bot_repetidas_thread.is_alive():
        bot_repetidas_thread.stop()
        # Esperar un momento para que el hilo detecte el cambio
        time.sleep(0.5)
        bot_repetidas_thread = None

