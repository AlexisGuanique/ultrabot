import os
import pyperclip
import pyautogui
import time
from database import get_cookie_by_id


last_cookie_id =8
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
            print("########################################################")
            print(f"Texto de la cookie con ID {last_cookie_id} copiado al portapapeles.")
            print("########################################################")

            pyautogui.hotkey("ctrl", "v")

            # Incrementar el ID para la próxima ejecución
            last_cookie_id += 1
        else:
            print(f"No se pudo obtener la cookie con ID {last_cookie_id}. Deteniendo el flujo.")
            return False  # Indica que ya no hay más cookies y el bucle debe detenerse
    else:
        print("InputArea no encontrada en pantalla. Asegúrate de que sea visible.")

    return True  # Indica que la ejecución fue exitosa

def click_image(image_path, confidence=0.8, offset_x=0, offset_y=0, description=""):

    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            click_x = location[0] + offset_x
            click_y = location[1] + offset_y
            pyautogui.click(click_x, click_y)
            print(f"Clic realizado en {description} ({click_x}, {click_y}).")
            return True 
        else:
            print(f"{description} no encontrada en pantalla. Continuando con el flujo.")
            pass
    except Exception as e:
        print(f"Error al intentar hacer clic en {description}: {e}")
        pass 
    return False 

def click_image_multiple(image_paths, confidence=0.8, offset_x=0, offset_y=0, description=""):
    for image_path in image_paths:
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
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
    return click_image_multiple(["images/ultraLogo.png", "images/ultraLogo2.png"], description="logo de ultra")


def click_add_account():
    return click_image_multiple(["images/agregarCuenta.png", "images/agregarCuentaIngles.png"], description="botón de agregar cuenta")


def click_panel_dropDown():
    return click_image("images/panelDesplegableDown.png", description="panel desplegable")


def click_panel_dropUp():
    return click_image("images/panelDesplegableUp.png", description="panel desplegable")


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

def click_refresh():
    return click_image("images/recargarPestana.png", description="botón de recargar ventana")

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


#! Verificacion de catchat
def close_catchat():
    try:
        location = pyautogui.locateCenterOnScreen("images/catchatAutenticacion.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el catchat
    except Exception:
        pass
    return False  # No se cerró el catchat

def close_catchat_espanol():
    try:
        location = pyautogui.locateCenterOnScreen("images/catchatAutenticacion2.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el catchat en español
    except Exception:
        pass
    return False  # No se cerró el catchat en español

def close_logueo():
    try:
        location = pyautogui.locateCenterOnScreen("images/logueoUsuarioContrasena.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el logueo
    except Exception:
        pass
    return False  # No se cerró el logueo

def close_logueo_english():
    try:
        location = pyautogui.locateCenterOnScreen("images/logueoUsuarioContrasenaEnglish.png", confidence=0.8)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el logueo en inglés
    except Exception:
        pass
    return False  # No se cerró el logueo en inglés

def close_codigo():
    try:
        location = pyautogui.locateCenterOnScreen("images/codigoVerificacion.png", confidence=1)
        print(location)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el código de verificación
    except Exception:
        pass
    return False  # No se cerró el código de verificación

def close_codigo_espanol():
    try:
        location = pyautogui.locateCenterOnScreen("images/codigoVerificacionEspanol.png", confidence=0.8)
        print(location)
        if location:
            close_location = pyautogui.locateCenterOnScreen("images/cerrarVentana.png", confidence=0.8)
            if close_location:
                pyautogui.click(close_location)
                return True  # Indica que se cerró el código de verificación
    except Exception:
        pass
    return False


#TODO FUNCION PARA CUANDO SE LOGUEA COMPLETA MI CUENTA (variante 1)
def secuencia_deslogueo():

    try:
        success = False

        if click_panel_dropUp():
            success = True
        time.sleep(2)

        if click_menu_me():
            success = True
        time.sleep(2)

        if click_sign_out():
            success = True
        time.sleep(3)

        if click_join_now():
            success = True
        time.sleep(3)

        if click_login():
            success = True
        time.sleep(5)

        if click_confirm_user():
            success = True
        time.sleep(6)

        if click_minimize_window():
            success = True
        time.sleep(2)

        print("Secuencia de deslogueo completada." if success else "Secuencia de deslogueo no completada.")
        return success

    except Exception as e:
        print(f"Error inesperado en secuencia_deslogueo: {e}")
        return False

# #TODO CUANDO SE LOGUEA DIRECTO (VARIANTE 2)
# def direct_login():

#     try:
#         time.sleep(2)
#         success = False

#         if click_panel_dropUp():
#             success = True
#         time.sleep(2)
    
#         if click_menu_me():
#             success = True
#         time.sleep(2)

#         if click_sign_out():
#             success = True
#         time.sleep(3)

#         if click_join_now():
#             success = True
#         time.sleep(3)

#         if click_login():
#             success = True
#         time.sleep(8)

#         if click_confirm_user():
#             success = True
#         time.sleep(8)

#         if click_minimize_window():
#             success = True
#         time.sleep(1)

#         print("Direct login completado." if success else "Direct login no completado.")
#         return success

#     except Exception as e:
#         print(f"Error inesperado en direct_login: {e}")
#         return False

#TODO Funcion para el caso de que la cuenta se desloguee (variante 3)
def secuencia_login():
    try:
        time.sleep(2)

        success = False 
        time.sleep(2)

        if click_join_now():
            success = True
        time.sleep(3)

        if click_login():
            success = True
        time.sleep(3)

        if click_confirm_user():
            success = True
        time.sleep(10)

        if click_minimize_window():
            success = True
        time.sleep(2)

        print("Login completado." if success else "logueo no completado.")
        return success

    except Exception as e:
        print(f"Error inesperado en complete_deslogout_sequence: {e}")
        return False

#TODO FUNCION EN CASO DE QUE PIDA LOCATION (VARIANTE 4)
# def secuencia_location():
    # try:
 
    #     image1_found = pyautogui.locateCenterOnScreen("images/", confidence=0.8) is not None
    #     time.sleep(2)

    #     image2_found = pyautogui.locateCenterOnScreen("images/imagesTest/uneteAhoraTest.png", confidence=0.8) is not None
    #     time.sleep(2)

    #     if not (image1_found or image2_found):
    #         print("No se detectaron imágenes. Saliendo de la función.")
    #         return False


    #     if image1_found or image2_found:
    #         print("Imagen detectada. Ejecutando la secuencia de deslogueo.")

    #     success = False  # Bandera para verificar si al menos una acción se realizó correctamente
        # time.sleep(2)

        # if click_join_now():
        #     success = True
        # time.sleep(3)

        # if click_login():
        #     success = True
        # time.sleep(3)

        # if click_confirm_user():
        #     success = True
        # time.sleep(8)

        # if click_minimize_window():
        #     success = True
        # time.sleep(2)

    #     print("Login completado." if success else "logueo no completado.")
    #     return success

    # except Exception as e:
    #     print(f"Error inesperado en complete_deslogout_sequence: {e}")
    #     return False

#TODO FUNCION PARA VERIFICAR EL CATCHAT, CODIGO, ETC (variante 5)
def close_verifications():
    time.sleep(2)
    if close_catchat():
        print("Catchat detectado y cerrado.")
        return True  # Sale inmediatamente después de encontrar y cerrar el Catchat
    time.sleep(2)

    if close_catchat_espanol():
        print("Catchat en español detectado y cerrado.")
        return True  # Sale inmediatamente después de encontrar y cerrar el Catchat en español
    time.sleep(2)

    if close_logueo():
        print("Logueo detectado y cerrado.")
        return True  # Sale inmediatamente después de encontrar y cerrar el logueo
    time.sleep(2)

    if close_logueo_english():
        print("Logueo en inglés detectado y cerrado.")
        return True  # Sale inmediatamente después de encontrar y cerrar el logueo en inglés
    time.sleep(2)

    if close_codigo():
        print("Código de verificación detectado y cerrado.")
        return True  # Sale inmediatamente después de encontrar y cerrar el código de verificación
    time.sleep(2)

    print("No se detectó ninguna verificación.")
    return False  # No se cerró ninguna ventana


def execute_ultra_bot():

    print("########################################################################")
    print("INICIANDO EL BOT ULTRA")
    print("########################################################################")
    click_ultra_logo()
    time.sleep(5)


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

        print("########################################################################")
        print("Pasaron los 40 segundos. Iniciando variantes")
        print("########################################################################")

        if click_confirm_user():
            print("confirmando usuario")
        time.sleep(8)
        
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

        if close_codigo():
            print("Código de verificación detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)

        if close_codigo_espanol():
            print("Código de verificación detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)
        
        #! variante 1
        # if secuencia_deslogueo():
        #     print("Secuencia de variante 1 realizada con exito. Reiniciando el bucle...")
        #     continue 
        # time.sleep(8)

        click_panel_dropUp()
        time.sleep(3)

        click_menu_me()
        time.sleep(3)

        click_sign_out()
        time.sleep(3)

        click_join_now()
        time.sleep(3)

        click_login()
        time.sleep(5)

        click_confirm_user()
        time.sleep(6)

        if click_minimize_window():
            print("Ventana principal detectada y minimizada.")
            continue
        time.sleep(2)
       

        # #! variante 3
        # if secuencia_login():
        #     print("Secuencia de variante 3 realizada con exito. Reiniciando el bucle...")
        #     continue 
        # time.sleep(8)

        time.sleep(2)

        click_join_now()
        time.sleep(3)

        click_login()
        time.sleep(3)

        click_confirm_user()
        time.sleep(10)

        if click_minimize_window():
            print("Ventana principal detectada y minimizada.")
            continue
        time.sleep(2)

        #! variante 5
        # if close_verifications():
        #     print("Secuencia de variante 5 realizada con exito. Reiniciando el bucle...")
        #     continue
        # time.sleep(5)

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

        if close_logueo_english():
            print("Logueo en inglés detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el logueo en inglés
        time.sleep(3)

        if close_codigo():
            print("Código de verificación detectado y cerrado.")
            continue  # Sale inmediatamente después de encontrar y cerrar el código de verificación
        time.sleep(3)
        
        break
