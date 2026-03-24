import threading
import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id, get_bot_settings, get_ultra_credentials, get_user_agent_by_id, clear_database, fetch_accounts_from_server, save_cookies_to_db, get_repetidas_settings, get_use_local_accounts, get_cookie_count
from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder, kill_ultra_processes
from app.ultrabot.cookie_convert import sync_ultra_partitions_network_cookies, count_partition_folders
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
    Espera y verifica que alguna de las imágenes de LinkedIn (linkedinDetected.PNG, linkedinDetected2.PNG,
    linkedinDetected3.png, linkedinDetected4.png) esté presente en la pantalla.
    Primero intenta buscar y hacer clic en los botones de europa (medida de seguridad para máquinas europeas),
    pero si no los encuentra, continúa buscando LinkedIn de todas formas (para máquinas no europeas).
    
    Args:
        max_attempts (int): Número máximo de intentos para verificar la imagen de europa
        wait_time (int): Tiempo de espera entre intentos en segundos (solo para buscar europa)
        confidence (float): Nivel de confianza para la detección (0.0 a 1.0)
    
    Returns:
        bool: True si la imagen de LinkedIn está presente, False si no
    """
    linkedin_image1 = "app/ultrabot/images/accionesVentana/linkedinDetected.PNG"
    linkedin_image2 = "app/ultrabot/images/accionesVentana/linkedinDetected2.PNG"
    linkedin_image3 = "app/ultrabot/images/accionesVentana/linkedinDetected3.png"
    linkedin_image4 = "app/ultrabot/images/accionesVentana/linkedinDetected4.png"
    europa_boton1 = "app/ultrabot/images/accionesVentana/ventanaGrisEuropa.png"
    europa_boton2 = "app/ultrabot/images/accionesVentana/ventanaGrisEuropa3.png"
    
    # Verificar que los archivos existan
    linkedin_path1 = get_resource_path(linkedin_image1)
    linkedin_path2 = get_resource_path(linkedin_image2)
    linkedin_path3 = get_resource_path(linkedin_image3)
    linkedin_path4 = get_resource_path(linkedin_image4)
    if not any(os.path.exists(p) for p in (linkedin_path1, linkedin_path2, linkedin_path3, linkedin_path4)):
        print(f"  ⚠️ Advertencia: No se encontraron las imágenes de LinkedIn en las rutas esperadas")
        print(f"     Buscado: {linkedin_path1}, {linkedin_path2}, {linkedin_path3}, {linkedin_path4}")
    
    # Paso 1: Buscar y hacer clic en los botones de europa (medida de seguridad opcional)
    europa_clicked = False
    europa_max_attempts = 3  # Menos intentos para europa, no es crítico
    
    for attempt in range(europa_max_attempts):
        # Buscar botones de europa
        europa_location1 = find_image(europa_boton1, confidence=0.9)
        europa_location2 = find_image(europa_boton2, confidence=0.9)
        
        if europa_location1:
            # Hacer clic en las coordenadas donde se encontró el botón
            try:
                pyautogui.click(europa_location1)
                time.sleep(0.2)  # Pequeña pausa después del clic
                europa_clicked = True
                print(f"  ✅ Botón de europa detectado y clic realizado (medida de seguridad)")
                break
            except Exception as e:
                pass
        elif europa_location2:
            # Hacer clic en las coordenadas donde se encontró el botón
            try:
                pyautogui.click(europa_location2)
                time.sleep(0.2)  # Pequeña pausa después del clic
                europa_clicked = True
                print(f"  ✅ Botón de europa (español) detectado y clic realizado (medida de seguridad)")
                break
            except Exception as e:
                pass
        
        if attempt < europa_max_attempts - 1:
            time.sleep(0.5)  # Espera más corta para europa
    
    # Si se hizo clic en europa, esperar 2 segundos antes de buscar LinkedIn
    if europa_clicked:
        print(f"  ⏳ Esperando 2 segundos después del clic en europa...")
        time.sleep(2)
    else:
        print(f"  ℹ️ Botones de europa no encontrados (máquina no europea), buscando LinkedIn directamente...")
    
    # Paso 2: Buscar LinkedIn (funciona tanto para máquinas europeas como no europeas)
    linkedin_max_attempts = max_attempts  # Usar el mismo número de intentos que se pasa como parámetro
    linkedin_wait_time = wait_time      # Usar el mismo tiempo de espera
    
    for attempt in range(linkedin_max_attempts):
        # Buscar todas las imágenes de LinkedIn
        linkedin_found1 = find_image(linkedin_image1, confidence=confidence)
        linkedin_found2 = find_image(linkedin_image2, confidence=confidence)
        linkedin_found3 = find_image(linkedin_image3, confidence=confidence)
        linkedin_found4 = find_image(linkedin_image4, confidence=confidence)
        
        if linkedin_found1 or linkedin_found2 or linkedin_found3 or linkedin_found4:
            which_image = (
                "linkedinDetected.PNG" if linkedin_found1 else
                "linkedinDetected2.PNG" if linkedin_found2 else
                "linkedinDetected3.png" if linkedin_found3 else "linkedinDetected4.png"
            )
            print(f"  ✅ LinkedIn detectado ({which_image}) en intento {attempt + 1}/{linkedin_max_attempts}")
            return True
        
        if attempt < linkedin_max_attempts - 1:
            time.sleep(linkedin_wait_time)
    
    print(f"  ❌ LinkedIn no detectado después de {linkedin_max_attempts} intentos (confianza: {confidence})")
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

def check_ultra_error_and_recover(max_attempts=5):
    """
    Verifica en cada iteración si estamos logueados Y si Ultra cargó correctamente.
    En cada intento verifica ambas cosas:
    1. Si estamos en la pantalla de login (necesita hacer login)
    2. Si encuentra las imágenes de carga correcta (Ultra cargó bien)
    
    Si NO encuentra ninguna de las dos cosas (o ambas fallan), cierra Ultra, espera 5 segundos,
    abre Ultra, espera 20 segundos, y vuelve a verificar ambas cosas.
    
    Si encuentra que está en login, hace login sin cerrar/abrir Ultra.
    Si encuentra las imágenes de carga correcta, retorna True.
    
    Args:
        max_attempts (int): Número máximo de intentos de recuperación
    
    Returns:
        bool: True si Ultra cargó correctamente (se encontró alguna imagen), False si falló después de todos los intentos
    """
    correct_load_images = [
        "app/ultrabot/images/accionesVentana/cargaCorrectaultra1.PNG",
        "app/ultrabot/images/accionesVentana/cargaCorrectaultra2.PNG"
    ]
    
    for attempt in range(max_attempts):
        print(f"🔍 Verificando login y carga de Ultra (intento {attempt + 1}/{max_attempts})...")

        # 1) Verificar si estamos en la pantalla de login (la cuenta se deslogueó)
        is_in_login = check_welcome_screen_visible(max_attempts=3, wait_time=0.5, confidence=0.7)
        
        # 2) Verificar si alguna de las imágenes de carga correcta está presente
        image_found = False
        for correct_image in correct_load_images:
            if find_image(correct_image, confidence=0.7):
                print(f"✅ Imagen de carga correcta detectada: {correct_image}")
                image_found = True
                break
        
        # Si encontramos la imagen de carga correcta, todo está bien
        if image_found:
            print("✅ Ultra cargó correctamente")
            return True
        
        # Si estamos en login, hacer login (sin cerrar/abrir Ultra)
        # Usar solo 1 intento de login para no gastar todos los intentos en una sola iteración
        if is_in_login:
            print("ℹ️ Pantalla de login detectada. La cuenta se deslogueó, realizando login nuevamente...")
            if not login_with_ultra_credentials_with_attempts(max_login_attempts=1, show_error_message=False):
                print("⚠️ No se pudo completar el login en este intento, continuando con el siguiente...")
                # No retornar False aquí, continuar al siguiente intento del bucle
                # para que pueda cerrar/abrir Ultra y volver a intentar
                if attempt < max_attempts - 1:
                    print("⚠️ No se detectó login ni imágenes de carga correcta. Cerrando y reabriendo Ultra...")
                    
                    # Cerrar Ultra
                    click_coordinates(1339, 10)
                    print("⏳ Esperando 5 segundos después de cerrar Ultra...")
                    time.sleep(5)
                    
                    # Abrir Ultra de nuevo
                    print("🔄 Abriendo Ultra nuevamente...")
                    if not click_ultra_logo(max_attempts=3, delay_between_attempts=1):
                        print("❌ No se pudo hacer clic en el logo de Ultra")
                        return False
                    
                    # Esperar 20 segundos para que Ultra se abra completamente
                    print("⏳ Esperando 20 segundos para que Ultra se abra completamente...")
                    time.sleep(20)
                    continue
                else:
                    print(f"❌ Ultra no cargó correctamente después de {max_attempts} intentos")
                    return False
            # Dar tiempo a que Ultra termine de cargar después del nuevo login
            print("⏳ Esperando 15 segundos después del nuevo login antes de volver a verificar...")
            time.sleep(15)
            # Continuar al siguiente intento del bucle para verificar de nuevo
            continue
        
        # Si llegamos aquí, NO estamos en login Y NO encontramos imágenes de carga correcta
        # Esto significa que Ultra no cargó bien, necesitamos cerrar y reabrir
        if attempt < max_attempts - 1:
            print("⚠️ No se detectó login ni imágenes de carga correcta. Cerrando y reabriendo Ultra...")
            
            # Cerrar Ultra
            click_coordinates(1339, 10)
            print("⏳ Esperando 5 segundos después de cerrar Ultra...")
            time.sleep(5)
            
            # Abrir Ultra de nuevo
            print("🔄 Abriendo Ultra nuevamente...")
            if not click_ultra_logo(max_attempts=3, delay_between_attempts=1):
                print("❌ No se pudo hacer clic en el logo de Ultra")
                return False
            
            # Esperar 20 segundos para que Ultra se abra completamente
            print("⏳ Esperando 20 segundos para que Ultra se abra completamente...")
            time.sleep(20)
        else:
            # Último intento falló
            print(f"❌ Ultra no cargó correctamente después de {max_attempts} intentos")
            return False
    
    # Si llegamos aquí, todos los intentos fallaron
    return False


# Antes de "Start all tabs": debe verse el marcador de LinkedIn cargado bien.
LINKEDIN_CARGA_BIEN_IMAGE = "app/ultrabot/images/accionesVentana/linkedincargabien.PNG"


def linkedin_carga_bien_visible(confidence: float = 0.65) -> bool:
    """True si en pantalla aparece el icono/recorte linkedincargabien.PNG."""
    return bool(find_image(LINKEDIN_CARGA_BIEN_IMAGE, confidence=confidence))


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
                    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                    time.sleep(40)
                    wait_for_login_interface(max_attempts=3, wait_time=15)
                continue
            
            # Esperar un momento después del login para que la pantalla se actualice
            time.sleep(3)
            
            # Verificar si welcomeUltra.PNG está visible (indica que el login falló)
            # Aumentamos a 8 intentos (3 originales + 5 adicionales) para mayor robustez
            if not check_welcome_screen_visible(max_attempts=8, wait_time=0.5, confidence=0.7):
                # Login exitoso (welcomeUltra.PNG no está visible)
                print("✅ Login exitoso confirmado después de múltiples verificaciones")
                return True
            
            # Si llegamos aquí, el login falló (welcomeUltra.PNG está visible)
            print(f"❌ Login falló en intento {login_attempt + 1}, reintentando...")
            # Si no es el último intento, cerrar ventana y reintentar
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                time.sleep(40)
                wait_for_login_interface(max_attempts=3, wait_time=15)
        except Exception as e:
            # Si hay una excepción, continuar al siguiente intento
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                time.sleep(40)
                wait_for_login_interface(max_attempts=3, wait_time=15)
            continue
    
    # Si llegamos aquí, todos los intentos fallaron
    print("❌ Login falló después de 5 intentos")
    messagebox.showerror(
        "Error de login",
        "No se pudo completar el login después de 5 intentos.\n\nVerifica tus credenciales y que Ultra esté funcionando correctamente."
    )
    return False

def login_with_ultra_credentials_with_attempts(max_login_attempts=1, show_error_message=False):
    """
    Realiza el login con las credenciales de Ultra con verificación y reintentos.
    Versión que permite especificar el número máximo de intentos de login.
    Esta función es para uso interno en check_ultra_error_and_recover().
    Verifica que el login fue exitoso comprobando que welcomeUltra.PNG no esté visible.
    
    Args:
        max_login_attempts (int): Número máximo de intentos de login (por defecto 1)
        show_error_message (bool): Si True, muestra mensaje de error al fallar. Si False, solo retorna False.
    
    Returns:
        bool: True si el login fue exitoso, False si falló después de max_login_attempts intentos
    """
    print(f"🔐 Iniciando proceso de login (máximo {max_login_attempts} intento(s))...")
    # 🧩 Flujo normal de login
    credentials = get_ultra_credentials()
    if not credentials:
        # Solo mostrar error si no hay credenciales (error crítico)
        if show_error_message:
            messagebox.showerror(
                "Credenciales faltantes",
                "Debes ingresar tu email y contraseña de Ultra.\n\nHazlo desde la interfaz de configuración y vuelve a ejecutar la aplicación."
            )
        return False

    email = credentials["email"]
    password = credentials["password"]
    
    # Intentar login hasta max_login_attempts veces
    max_attempts = max_login_attempts
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
                    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                    time.sleep(40)
                    wait_for_login_interface(max_attempts=3, wait_time=15)
                continue
            
            # Esperar un momento después del login para que la pantalla se actualice
            time.sleep(3)
            
            # Verificar si welcomeUltra.PNG está visible (indica que el login falló)
            # Aumentamos a 8 intentos (3 originales + 5 adicionales) para mayor robustez
            if not check_welcome_screen_visible(max_attempts=8, wait_time=0.5, confidence=0.7):
                # Login exitoso (welcomeUltra.PNG no está visible)
                print("✅ Login exitoso confirmado después de múltiples verificaciones")
                return True
            
            # Si llegamos aquí, el login falló (welcomeUltra.PNG está visible)
            print(f"❌ Login falló en intento {login_attempt + 1}, reintentando...")
            # Si no es el último intento, cerrar ventana y reintentar
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                time.sleep(40)
                wait_for_login_interface(max_attempts=3, wait_time=15)
        except Exception as e:
            # Si hay una excepción, continuar al siguiente intento
            if login_attempt < max_attempts - 1:
                click_coordinates(1339, 10)
                time.sleep(2)
                click_ultra_logo(max_attempts=3, delay_between_attempts=1)
                print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                time.sleep(40)
                wait_for_login_interface(max_attempts=3, wait_time=15)
            continue
    
    # Si llegamos aquí, todos los intentos fallaron
    print(f"❌ Login falló después de {max_login_attempts} intento(s)")
    if show_error_message:
        messagebox.showerror(
            "Error de login",
            f"No se pudo completar el login después de {max_login_attempts} intento(s).\n\nVerifica tus credenciales y que Ultra esté funcionando correctamente."
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
    
    # Verificar que hay cookies disponibles antes de intentar leer
    cookie_count = get_cookie_count()
    if cookie_count == 0:
        print(f"❌ No hay cookies disponibles en la base de datos")
        messagebox.showerror("Error", "No hay cookies disponibles en la base de datos. El bot se detendrá.")
        stop_ultra_bot()
        return False
    
    print(f"🔍 Buscando cookie con ID {cookie_id_to_use} (Total de cookies disponibles: {cookie_count})")
    cookie_text = get_cookie_by_id(cookie_id_to_use)

    if not cookie_text:
        print(f"❌ No se encontró cookie con ID {cookie_id_to_use}. Total de cookies disponibles: {cookie_count}")
        # Intentar obtener el ID mínimo disponible
        from app.database.database import DB_PATH
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT MIN(id) FROM cookies')
            min_id = cursor.fetchone()[0]
            conn.close()
            
            if min_id:
                print(f"⚠️ El ID mínimo disponible es {min_id}, pero se intentó usar {cookie_id_to_use}")
                messagebox.showerror("Error", f"No se encontró cookie con ID {cookie_id_to_use}. El ID mínimo disponible es {min_id}. Total de cookies: {cookie_count}.")
            else:
                messagebox.showerror("Error", f"No se encontró cookie con ID {cookie_id_to_use}. No hay cookies disponibles en la base de datos.")
        except Exception as e:
            print(f"⚠️ Error al verificar IDs disponibles: {e}")
            messagebox.showerror("Error", f"No se encontró cookie con ID {cookie_id_to_use}. Total de cookies: {cookie_count}.")
        
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

        # ✔️ Navegar al botón OK/Save con Tab 4 veces y presionar Enter
        print("✔️ Navegando al botón OK/Save...")
        for _ in range(4):
            pyautogui.press("tab")
            time.sleep(0.2)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(2)

    # 🔄 Función auxiliar para verificar si la cookie es inválida (más robusta)
    def check_cookie_invalid(max_checks=4, wait_between_checks=0.3, confidence=0.7):
        """Verifica múltiples veces si la imagen de cookie inválida o user agent no válido está presente"""
        cookie_no_valida_path = "app/ultrabot/images/ingresarCookie/cookieNoValidaNueva.png"
        user_agent_no_valido_path = "app/ultrabot/images/ingresarCookie/userAgentNoValido.PNG"
        cookie_detection_count = 0
        user_agent_detection_count = 0
        
        for _ in range(max_checks):
            if find_image(cookie_no_valida_path, confidence=confidence):
                cookie_detection_count += 1
            if find_image(user_agent_no_valido_path, confidence=confidence):
                user_agent_detection_count += 1
            time.sleep(wait_between_checks)
        
        # Si cualquiera de las dos se detectó al menos 2 veces, consideramos que está presente
        return cookie_detection_count >= 2 or user_agent_detection_count >= 2

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
            print(f"⚠️ Cookie o User Agent no válido detectado en intento {attempt}")
            
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
    #! Son 171
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


def click_ultra_internal_config():
    """Aplica la configuración interna inicial antes de agregar cuentas."""
    default_settings_image = "app/ultrabot/images/configuracion/defaultsettings.PNG"
    max_retries = 10

    # Clic inicial para abrir configuración.
    if not click_coordinates(1328, 45):
        return False

    time.sleep(1.2)

    # Validar imagen; si no aparece, reintentar clic hasta 10 veces.
    for _ in range(max_retries):
        if find_image(default_settings_image, confidence=0.7):
            break
        click_coordinates(1328, 45)
        time.sleep(1.2)
    else:
        return False

    # Con la pantalla detectada, hacer clic en la opción requerida.
    clicked = click_image_multiple(
        [default_settings_image],
        description="opción de configuración interna",
        fallback_coords="854 x 208",
        confidence=0.7
    )

    if not clicked:
        return False

    time.sleep(1.0)

    # Enfocar input de User Agent.
    if not click_coordinates(651, 354):
        return False

    time.sleep(0.8)

    # Obtener User Agent guardado en configuración del bot y pegarlo en el input.
    config = get_bot_settings()
    user_agent = ""
    if config:
        user_agent = str(config.get("user_agent", "")).strip()

    if not user_agent:
        print("⚠️ No hay User Agent configurado en ajustes del bot.")
        return False

    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.5)
    pyperclip.copy(user_agent)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.3)

    # Clics adicionales de configuración.
    if not click_coordinates(452, 274):
        return False
    time.sleep(0.9)

    if not click_coordinates(452, 498):
        return False
    time.sleep(0.9)

    # Buscar botón Save y confirmarlo.
    save_button_image = "app/ultrabot/images/configuracion/saveboton.PNG"
    time.sleep(1.0)
    if find_image(save_button_image, confidence=0.7):
        time.sleep(0.6)
        return click_coordinates(931, 608)

    return False


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
        """Detiene el bot de forma segura"""
        print("🛑 Deteniendo bot...")
        self.running = False
    
    def safe_sleep(self, seconds, check_interval=0.5):
        """Duerme de forma segura, verificando self.running periódicamente"""
        elapsed = 0
        while elapsed < seconds and self.running:
            sleep_time = min(check_interval, seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
        return self.running

    def run(self):
        global last_cookie_id
        print("\n" + "="*60)
        print("🚀 INICIANDO ULTRA BOT")
        print("="*60)
        print("⏳ Esperando 3 segundos antes de comenzar...")
        if not self.safe_sleep(3):
            print("🛑 Bot detenido antes de iniciar")
            return
        
        # Verificar ANTES de buscar el logo
        if not self.running:
            print("🛑 Bot detenido antes de buscar logo")
            return
        
        print("🖱️ Buscando logo de Ultra...")
        # Reducir intentos para que responda más rápido si se detiene
        if not click_ultra_logo(max_attempts=3, delay_between_attempts=1):
            # Verificar si fue porque se detuvo el bot
            if not self.running:
                print("🛑 Bot detenido durante búsqueda del logo")
                return
            messagebox.showerror("Error", "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.")
            print("❌ No se pudo hacer clic en el logo de Ultra")
            return
        print("✅ Logo de Ultra encontrado y clickeado")
        
        # Verificar inmediatamente después del clic
        if not self.running:
            print("🛑 Bot detenido después de hacer clic en logo")
            return
        
        print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
        if not self.safe_sleep(40):
            print("🛑 Bot detenido durante espera inicial")
            return
        print("✅ Espera inicial completada")
        # click_europa_boton()
        # time.sleep(1)
        # click_europa_boton2()

        # login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
        print("🔐 Iniciando proceso de login en Ultra...")
        if not login_with_ultra_credentials():
            print("❌ Login fallido")
            return  # El mensaje de error ya fue mostrado por login_with_ultra_credentials()
        
        if not self.running:
            print("🛑 Bot detenido después de login")
            return
        print("✅ Login exitoso en Ultra")
        
        print("⏳ Esperando 15 segundos después del login...")
        if not self.safe_sleep(15):
            print("🛑 Bot detenido durante espera post-login")
            return
        print("✅ Espera post-login completada")
        
        # Verificar errores de Ultra y recuperar si es necesario
        print("\n🔍 Verificando que Ultra haya cargado correctamente...")
        if not check_ultra_error_and_recover(max_attempts=5):
            print("❌ Ultra no cargó correctamente después de múltiples intentos")
            messagebox.showerror("Error de Ultra", "Ultra no está cargando correctamente después del login. El proceso se detendrá.")
            return
        
        if not self.running:
            print("🛑 Bot detenido después de verificación de errores de Ultra")
            return
        
        print("✅ Ultra cargó correctamente, continuando con el ciclo normal...")

        print("\n📋 Obteniendo configuración del bot...")
        config = get_bot_settings()

        if config:
            MAX_ITERATIONS = config["iterations"]
            TIEMPO_ESPERA = config["interval_seconds"]
        else:
            MAX_ITERATIONS = 16
            TIEMPO_ESPERA = 7200

        # Verificar si se deben usar cuentas locales
        use_local = get_use_local_accounts()
        
        print(f"⚙️ Configuración cargada:")
        print(f"   - Iteraciones: {MAX_ITERATIONS}")
        print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
        if use_local:
            print("📦 Modo: Usando cuentas de la base de datos local")
        else:
            print("🌐 Modo: Obteniendo cuentas del servidor")
        
        iteration_count = 0
        # Tras cargar cookies en lote (sync a disco), se rellena y se iguala iteration_count
        # para disparar el mismo bloque que antes (una iteración por cuenta hasta MAX_ITERATIONS).
        pending_activation_batch = None  # int o None: cuentas listas para activar tabs
        print("\n🔄 Iniciando bucle principal de procesamiento...")

        
        # Calcular y enviar la próxima hora del ciclo al servidor
        try:
            from datetime import datetime, timedelta
            from app.auth.auth import send_status_update_with_next_cycle
            
            # Calcular la próxima hora del ciclo: ahora + TIEMPO_ESPERA segundos
            next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
            print(f"📅 Calculando próximo ciclo...")
            print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
            print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Enviar al servidor usando la función auxiliar
            send_status_update_with_next_cycle('running', next_cycle)
            print(f"✅ Próximo ciclo enviado al servidor correctamente")
        except Exception as e:
            print(f"⚠️  Error al calcular/enviar próxima hora del ciclo: {e}")
            import traceback
            traceback.print_exc()

        # Cargar cuentas según la preferencia
        if use_local:
            # Usar cuentas locales
            local_count = get_cookie_count()
            if local_count == 0:
                print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
                use_local = False
            else:
                print(f"📦 Usando {local_count} cuentas de la base de datos local")
                if local_count < MAX_ITERATIONS:
                    print(f"⚠️ Solo hay {local_count} cuentas locales, pero se necesitan {MAX_ITERATIONS}")
                # Asegurar que last_cookie_id esté en 1 cuando se usan cuentas locales
                last_cookie_id = 1
                print(f"🔄 last_cookie_id inicializado en {last_cookie_id} para modo local")
        
        if not use_local:
            # Obtener cuentas del servidor
            print("🗑️ Limpiando base de datos...")
            clear_database()
            print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
            accounts = fetch_accounts_from_server(MAX_ITERATIONS)
            
            if not accounts:
                messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                return
            
            print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
            save_cookies_to_db(accounts)
            
            # Verificar que las cookies se guardaron correctamente
            saved_count = get_cookie_count()
            if saved_count == 0:
                messagebox.showerror("Error", f"No se pudieron guardar las cuentas en la base de datos. Se obtuvieron {len(accounts)} cuentas pero no se guardaron.")
                return
            print(f"✅ Se guardaron {saved_count} cuentas en la base de datos")
            
            # Asegurar que last_cookie_id esté en 1 después de limpiar la base de datos
            last_cookie_id = 1
            print(f"🔄 last_cookie_id inicializado en {last_cookie_id}")

        while self.running:
            # Verificar periódicamente si se debe detener
            if not self.running:
                print("🛑 Bot detenido - saliendo del bucle principal")
                break
            
            if iteration_count >= MAX_ITERATIONS or (
                pending_activation_batch is not None
                and iteration_count >= pending_activation_batch
            ):
                if not self.running:
                    print("🛑 Bot detenido antes de procesar tabs")
                    break

                work_batch = (
                    pending_activation_batch
                    if pending_activation_batch is not None
                    else MAX_ITERATIONS
                )
                pending_activation_batch = None

                print(
                    f"\n📊 Carga de cookies completada ({work_batch} cuenta(s)). "
                    f"Iniciando proceso de tabs (activación)..."
                )

                # Antes de "Start all tabs": solo linkedincargabien.PNG debe estar visible.
                # Si no: cerrar Ultra, reabrir, esperar 30 s, verificar login/carga y reintentar (máx. 5).
                LINKEDIN_PRE_START_MAX_RETRIES = 5
                POLL_INTERVAL = 0.5
                POLL_SECONDS_PER_ATTEMPT = 20.0  # ventana de búsqueda tras Europa antes de reiniciar
                activation_ready = False
                for load_attempt in range(LINKEDIN_PRE_START_MAX_RETRIES):
                    if not self.running:
                        break
                    if load_attempt > 0:
                        print(
                            f"🔄 Reintentando detección de linkedincargabien "
                            f"({load_attempt + 1}/{LINKEDIN_PRE_START_MAX_RETRIES})..."
                        )

                    click_europa_boton()
                    if not self.safe_sleep(1):
                        break
                    click_europa_boton2()
                    if not self.safe_sleep(2):
                        break

                    print(
                        f"🔍 Buscando {LINKEDIN_CARGA_BIEN_IMAGE} (hasta {POLL_SECONDS_PER_ATTEMPT:.0f}s)..."
                    )
                    _polls = max(1, int(POLL_SECONDS_PER_ATTEMPT / POLL_INTERVAL))
                    seen_linkedin = False
                    for _ in range(_polls):
                        if not self.running:
                            break
                        if linkedin_carga_bien_visible(confidence=0.65):
                            print(
                                "✅ linkedincargabien detectado. Continuando con Start all tabs..."
                            )
                            seen_linkedin = True
                            break
                        if not self.safe_sleep(POLL_INTERVAL):
                            break

                    if seen_linkedin:
                        activation_ready = True
                        break

                    print(
                        "⚠️ No se detectó linkedincargabien; cerrando Ultra, reabriendo y "
                        f"esperando 30 s antes de volver a verificar..."
                    )
                    if load_attempt >= LINKEDIN_PRE_START_MAX_RETRIES - 1:
                        break

                    # Cerrar ventana primero; luego esperar y recién ahí terminar procesos (evita locks).
                    click_coordinates(1339, 10)
                    print("⏳ Esperando 5 s tras cerrar la ventana antes de terminar procesos de Ultra...")
                    if not self.safe_sleep(5):
                        break
                    try:
                        kill_ultra_processes(show_confirmation=False)
                    except Exception as e:
                        print(f"⚠️ Error al terminar procesos de Ultra: {e}")
                        import traceback

                        traceback.print_exc()

                    print("🔄 Abriendo Ultra de nuevo (logo)...")
                    if not click_ultra_logo(max_attempts=3, delay_between_attempts=1):
                        print("❌ No se pudo hacer clic en el logo de Ultra")
                        break

                    print("⏳ Esperando 30 s para que Ultra estabilice tras reabrir...")
                    if not self.safe_sleep(30):
                        break

                    if not check_ultra_error_and_recover(max_attempts=5):
                        print(
                            "⚠️ Ultra no pasó la verificación tras el reinicio; "
                            "se intentará de nuevo..."
                        )

                if not activation_ready:
                    if self.running:
                        messagebox.showerror(
                            "LinkedIn / Ultra",
                            "No se pudo detectar linkedincargabien.PNG después de varios intentos.\n\n"
                            "No se ejecutará Start all tabs.",
                        )
                    break

                click_start_all_tabs()
                if not self.safe_sleep(2):
                    break
                click_europa_boton()
                if not self.safe_sleep(1):
                    break
                click_europa_boton2()

                if not click_acept_actionTabs():
                    if not self.safe_sleep(1):
                        break
                    click_acept_actionTabs()

                tiempo_por_parte = TIEMPO_ESPERA // 4
                print(f"⏳ Esperando {tiempo_por_parte}s por parte (total: {TIEMPO_ESPERA}s)")
                if not self.safe_sleep(tiempo_por_parte):
                    print("🛑 Bot detenido durante espera de tabs")
                    break
                
                # Constantes para el manejo de errores de LinkedIn
                ERROR_LINKEDIN_PATH = "app/ultrabot/images/accionesVentana/ErrorLinkedin.PNG"
                MAX_INTENTOS_ERROR = 10
                COORD_ERROR_CLOSE = (915, 438)
                
                for parte in range(3):
                    if not self.running:
                        print("🛑 Bot detenido durante procesamiento de partes")
                        break
                        
                    print(f"📍 Procesando parte {parte + 1}/3...")
                    # Primero cerrar la ventana de Ultra
                    click_coordinates(1339, 10)
                    if not self.safe_sleep(5):
                        break
                    
                    # Luego eliminar los procesos de Ultra después de cerrar la ventana
                    # Envolver kill_ultra_processes en try-except para evitar que cierre el bot
                    try:
                        kill_ultra_processes(show_confirmation=False)
                    except Exception as e:
                        print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                        import traceback
                        traceback.print_exc()

                    for intento_error in range(MAX_INTENTOS_ERROR):
                        if not self.running:
                            break
                        click_ultra_logo()
                        if not self.safe_sleep(3):
                            break
                        
                        if not find_image(ERROR_LINKEDIN_PATH, confidence=0.7):
                            break
                        
                        click_coordinates(*COORD_ERROR_CLOSE)
                        if not self.safe_sleep(1):
                            break
                    
                    if not self.running:
                        break
                    
                    if not self.safe_sleep(15):
                        break

                    click_start_all_tabs() 
                    if not self.safe_sleep(2):
                        break
                    if not click_acept_actionTabs():
                        if not self.safe_sleep(1):
                            break
                        click_acept_actionTabs()                
                    
                    if not self.safe_sleep(tiempo_por_parte):
                        print("🛑 Bot detenido durante espera de parte")
                        break


                if not self.running:
                    break
                    
                click_europa_boton()
                if not self.safe_sleep(1):
                    break
                click_europa_boton2()
                

                print("⏹️ Deteniendo todas las tabs...")
                click_stop_all_tabs()
                if not self.safe_sleep(2):
                    break

                if not click_acept_stop_actionTabs():
                    if not self.safe_sleep(1):
                        break
                    click_acept_stop_actionTabs()
                    if not self.safe_sleep(2):
                        break

                print(f"🗑️ Cerrando {work_batch} ventanas...")
                if not self.safe_sleep(2):
                    break
                for _ in range(work_batch):
                    if not self.running:
                        break
                    click_close_window()
                    if not self.safe_sleep(0.5):
                        break

                if not self.running:
                    break
                    
                click_coordinates(1339, 10)
                if not self.safe_sleep(5):
                    break
                
                print("🔪 Eliminando procesos de Ultra...")
                # Envolver kill_ultra_processes en try-except para evitar que cierre el bot
                try:
                    kill_ultra_processes(show_confirmation=False)
                except Exception as e:
                    print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                    import traceback
                    traceback.print_exc()
                
                print("🗑️ Eliminando cache de Ultra...")
                cache_deleted = False
                max_cache_attempts = 3
                
                for cache_attempt in range(max_cache_attempts):
                    cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                    
                    if cache_deleted:
                        print("✅ Cache eliminada")
                        break
                    else:
                        if cache_attempt < max_cache_attempts - 1:
                            if not self.safe_sleep(5):
                                break
                            try:
                                kill_ultra_processes(show_confirmation=False)
                            except Exception as e:
                                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                
                if not cache_deleted:
                    messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                    break
                
                print("🔄 Reiniciando login...")
                max_restart_attempts = 3
                login_successful = False
                
                for restart_attempt in range(max_restart_attempts):
                    print(f"🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                    if click_ultra_logo():
                        print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                        time.sleep(40)
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
                                try:
                                    kill_ultra_processes(show_confirmation=False)
                                except Exception as e:
                                    print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                                cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                    else:
                        if restart_attempt < max_restart_attempts - 1:
                            click_coordinates(1339, 10)
                            time.sleep(5)
                            try:
                                kill_ultra_processes(show_confirmation=False)
                            except Exception as e:
                                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                
                if not login_successful:
                    messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                    break
                
                print("🔄 Reiniciando ciclo...")
                
                # Calcular y enviar la nueva próxima hora del ciclo al servidor
                try:
                    from datetime import datetime, timedelta
                    from app.auth.auth import send_status_update_with_next_cycle
                    
                    # Calcular la próxima hora del ciclo: ahora + TIEMPO_ESPERA segundos
                    next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
                    print(f"📅 Recalculando próximo ciclo después de reinicio...")
                    print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
                    print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Enviar al servidor usando la función auxiliar
                    send_status_update_with_next_cycle('running', next_cycle)
                    print(f"✅ Próximo ciclo recalculado y enviado al servidor correctamente")
                except Exception as e:
                    print(f"⚠️  Error al recalcular/enviar próxima hora del ciclo: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Verificar nuevamente si se deben usar cuentas locales
                use_local = get_use_local_accounts()
                
                if use_local:
                    local_count = get_cookie_count()
                    if local_count == 0:
                        print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
                        use_local = False
                    else:
                        print(f"📦 Usando {local_count} cuentas de la base de datos local")
                
                if not use_local:
                    clear_database()
                    print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
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

            if not self.running:
                print("🛑 Bot detenido durante el bucle principal")
                break

            # Fase 1 (iteration_count == 1 tras el incremento): configuración → pestañas →
            # cerrar Ultra → kill → sincronizar Cookies en disco. Luego iteration_count pasa
            # a batch_size y se dispara el bloque de activación de tabs (arriba).
            if iteration_count != 1:
                print(
                    "⚠️ iteration_count inesperado en fase de carga de cookies; "
                    f"esperado 1, recibido {iteration_count}. Deteniendo."
                )
                break

            # Todas las filas en BD (servidor o local): una pestaña/partición por cookie.
            batch_size = get_cookie_count()
            if batch_size == 0:
                messagebox.showerror(
                    "Error",
                    "No hay cuentas en la base de datos para sincronizar con Partitions.",
                )
                break
            if batch_size != MAX_ITERATIONS:
                print(
                    f"ℹ️ Cuentas en BD ({batch_size}) ≠ iteraciones configuradas ({MAX_ITERATIONS}). "
                    f"Se abrirán {batch_size} pestañas y se validará contra {batch_size} particiones."
                )

            print(
                f"🔄 Iteración {iteration_count}/{MAX_ITERATIONS}: "
                f"lote de {batch_size} cuenta(s) en BD — fila i (ORDER BY id) → partición i (orden creación)."
            )

            click_ultra_internal_config()

            time.sleep(2)
            for tab_i in range(batch_size):
                if not self.running:
                    break
                click_add_account()
                if tab_i < batch_size - 1:
                    time.sleep(2)

            if not self.running:
                break
            time.sleep(5)
            if not self.safe_sleep(2):
                break
            click_coordinates(1339, 10)

            if not self.safe_sleep(2):
                break

            # Dar tiempo a que suelte handles; Ultra a veces sigue usando Cookies tras cerrar la ventana.
            print("⏳ Esperando antes de forzar cierre de procesos de Ultra...")
            if not self.safe_sleep(4):
                break

            try:
                kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al terminar procesos de Ultra (continuando): {e}")
                import traceback
                traceback.print_exc()

            print("⏳ Esperando a que el sistema libere los archivos Cookies...")
            if not self.safe_sleep(5):
                break

            # Ultra a veces tarda en crear carpetas bajo Partitions tras cerrar; reintentar el conteo.
            print(
                "⏳ Esperando a que existan carpetas en Partitions (puede tardar unos segundos)..."
            )
            if not self.safe_sleep(5):
                break

            n_db = get_cookie_count()
            PARTITION_POLL_INTERVAL = 3.0
            PARTITION_POLL_MAX_ROUNDS = 20  # hasta ~60 s extra además de la espera previa
            n_part = 0
            for poll_round in range(PARTITION_POLL_MAX_ROUNDS):
                if not self.running:
                    break
                n_part = count_partition_folders()
                print(
                    f"📂 Partitions: {n_part} carpetas | BD: {n_db} filas | "
                    f"lote esperado: {batch_size} (comprobación {poll_round + 1}/{PARTITION_POLL_MAX_ROUNDS})"
                )
                if n_part >= batch_size:
                    print("✅ Número de particiones ≥ lote esperado.")
                    break
                if poll_round < PARTITION_POLL_MAX_ROUNDS - 1:
                    if not self.safe_sleep(PARTITION_POLL_INTERVAL):
                        break

            # Flexible: sincronizar tantas parejas como permita min(BD, Partitions); no abortar si falta 1 carpeta.
            if n_db != batch_size:
                print(
                    f"⚠️ Filas en BD ({n_db}) ≠ lote inicial ({batch_size}); se usará min(BD, particiones)."
                )

            if n_part == 0:
                messagebox.showerror(
                    "Error de Partitions",
                    "No hay ninguna carpeta bajo Partitions después de esperar.\n\n"
                    "Ultra no creó particiones o la ruta no es accesible. No se puede sincronizar.",
                )
                break

            n_sync = min(n_db, n_part)
            if n_part < batch_size:
                messagebox.showwarning(
                    "Particiones incompletas",
                    "Ultra aún no generó todas las carpetas de partición.\n\n"
                    f"• Carpetas detectadas: {n_part}\n"
                    f"• Cuentas en lote: {batch_size}\n\n"
                    f"Se sincronizarán solo las primeras {n_sync} parejas (BD ↔ partición). "
                    "El resto de cuentas quedará en BD sin escribir en disco en esta pasada.",
                )
            elif n_part > batch_size:
                print(
                    f"ℹ️ Hay más carpetas en Partitions ({n_part}) que cuentas en el lote ({batch_size}); "
                    f"la sincronización usará las primeras {batch_size} parejas por orden (BD / creación)."
                )

            if n_sync == 0:
                messagebox.showerror(
                    "Error",
                    "No hay parejas BD–partición para sincronizar (n_sync=0).",
                )
                break

            print("\n📂 Sincronizando archivos Cookies en cada carpeta Network desde la base de datos...")
            sync_code = sync_ultra_partitions_network_cookies()
            if sync_code < 0:
                print("❌ No se pudo completar la sincronización de cookies en disco.")
                break

            print(
                "\n✅ Cookies escritas en disco. Pasando a activación de cuentas (proceso de tabs)..."
            )
            click_ultra_logo()
            if not self.safe_sleep(3):
                break
            time.sleep(600)
            # Activación con el número real de cuentas sincronizadas a particiones (puede ser < batch_size).
            pending_activation_batch = n_sync
            iteration_count = n_sync
            continue

def execute_ultra_bot():
    """Inicia el bot en un hilo separado."""
    global bot_thread

    if bot_thread and bot_thread.is_alive():
        print("⚠️ El bot ya está corriendo. No se puede iniciar otro.")
        return

    print("\n" + "="*60)
    print("🚀 EJECUTANDO ULTRA BOT")
    print("="*60)
    print("📝 Creando hilo del bot...")
    bot_thread = UltraBotThread()
    print("✅ Hilo creado, iniciando ejecución...")
    bot_thread.start()
    print("✅ Hilo iniciado correctamente")


def stop_ultra_bot():
    """Detiene el bot y espera a que termine."""
    global bot_thread
    if bot_thread is not None and bot_thread.is_alive():
        print("🛑 Deteniendo bot...")
        bot_thread.stop()
        # Esperar hasta que el hilo realmente termine (máximo 5 segundos)
        max_wait = 5
        waited = 0
        while bot_thread is not None and bot_thread.is_alive() and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5
        
        if bot_thread is not None and bot_thread.is_alive():
            print("⚠️ El bot no se detuvo completamente, pero se marcó para detenerse")
        else:
            print("✅ Bot detenido completamente")
        
        bot_thread = None
    else:
        print("ℹ️ El bot no está corriendo")


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
        
        print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
        time.sleep(40)
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
            try:
                processes_killed = kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                processes_killed = False
            
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
                        try:
                            kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
            
            if not cache_deleted:
                messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                break
            
            print("🔄 Reintentando login después de limpieza...")
            max_restart_attempts = 3
            login_successful = False
            
            for restart_attempt in range(max_restart_attempts):
                print(f"  🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                if click_ultra_logo():
                    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                    time.sleep(40)
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
                            try:
                                kill_ultra_processes(show_confirmation=False)
                            except Exception as e:
                                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                            cache_deleted = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                else:
                    if restart_attempt < max_restart_attempts - 1:
                        click_coordinates(1339, 10)
                        time.sleep(5)
                        try:
                            kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
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

