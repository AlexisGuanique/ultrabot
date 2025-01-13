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

        cookie_id = 1
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


def handle_authentication_window():

    # Rutas de las imágenes
    catchat_autenticacion_path = "images/catchatAutenticacion.png"
    codigo_verificacion_path = "images/codigoVerificacion.png"
    logueo_usuario_path = "images/logueoUsuarioContrasena.png"

    try:
        catchat_autenticacion_location = pyautogui.locateCenterOnScreen(catchat_autenticacion_path, confidence=0.8)
        codigo_verificacion_location = pyautogui.locateCenterOnScreen(codigo_verificacion_path, confidence=0.8)
        logueo_usuario_location = pyautogui.locateCenterOnScreen(logueo_usuario_path, confidence=0.8)

        # Evaluar si se detectó alguna imagen
        if catchat_autenticacion_location is not None:
            print("Captcha encontrado.")
            return True
        elif codigo_verificacion_location is not None:
            print("Código de verificación encontrado.")
            return True
        elif logueo_usuario_location is not None:
            print("Logueo de usuario encontrado.")
            return True
        else:
            print("No se detectó ninguna ventana de autenticación o código de verificación.")
            return False

    except Exception as e:
        print(f"Error durante la verificación de imágenes: {e}")
        return False


def execute_ultra_bot():
    #! Le da click al boton de la aplicacion de ultra
    image_path = "images/ultraLogo.png"
    image_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

    if image_location is not None:
        print(
            f"Primera imagen encontrada en {image_location}. Realizando clic...")
        pyautogui.click(image_location)
        print(f"Clic realizado al logo de ultra.")
    else:
        print("Primera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    time.sleep(6)

    #! Le da al boton de abrir una pestaña nueva
    second_image_path = "images/agregarCuenta.png"
    for i in range(1):
        second_image_location = pyautogui.locateCenterOnScreen(
            second_image_path, confidence=0.8)

        if second_image_location is not None:
            print("Clic en agregar cuenta")
            pyautogui.click(second_image_location)
            time.sleep(0.1)
        else:
            print(
                "Segunda imagen no encontrada en pantalla. Asegúrate de que sea visible.")
            break

    time.sleep(10)

    #! Abre el panel desplegable
    quinta_image_path = "images/panelDesplegable.png"
    quinta_image_location = pyautogui.locateCenterOnScreen(
        quinta_image_path, confidence=0.8)

    if quinta_image_location is not None:
        print(
            f"Tercera imagen encontrada en {quinta_image_location}. Realizando clic...")
        pyautogui.click(quinta_image_location)
        print(f"Clic realizado al panel desplegable")
    else:
        print("Tercera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    time.sleep(1)

    #! Le da al boton de agregar una cookie
    fourth_image_path = "images/ingresarCookies.png"
    fourth_image_location = pyautogui.locateCenterOnScreen(
        fourth_image_path, confidence=0.8)

    if fourth_image_location is not None:
        print(
            f"Cuarta imagen encontrada en {fourth_image_location}. Realizando clic...")
        pyautogui.click(fourth_image_location)
        print(f"Clic realizado al logo de ingresar cookie.")
    else:
        print("Cuarta imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    time.sleep(1)

    #! Se agrega la cookie
    find_and_click_input()

    time.sleep(1)

    #! Se le da clic al boton de Ok despues de pegar la cookie
    quinta_image_path = "images/botonOk.png"
    quinta_image_location = pyautogui.locateCenterOnScreen(
        quinta_image_path, confidence=0.8)

    if quinta_image_location is not None:
        print(
            f"Tercera imagen encontrada en {quinta_image_location}. Realizando clic...")
        pyautogui.click(quinta_image_location)
        print(f"Clic realizado en la quinta imagen.")
    else:
        print("Tercera imagen no encontrada en pantalla. Asegúrate de que sea visible.")
        return

    time.sleep(25)

    #! En caso de que tengas que confirmar el usuario, se da clic un poco mas abajo de la imagen
    sexta_imagen_path = "images/confirmarUsuario.png"
    sexta_imagen_location = pyautogui.locateCenterOnScreen(
        sexta_imagen_path, confidence=0.8)

    if sexta_imagen_location is not None:
        print(
            f"Sexta imagen encontrada en {sexta_imagen_location}. Preparando clic debajo...")

        offset_y = 120
        click_x = sexta_imagen_location[0]
        click_y = sexta_imagen_location[1] + offset_y

        pyautogui.click(click_x, click_y)
        print(
            f"Clic realizado debajo de la sexta imagen en ({click_x}, {click_y}).")
    else:
        print("Sexta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(10)


    if handle_authentication_window():
        print("Acción requerida para manejar ventana de autenticación.")
        print("Holaaaaa como estas? Encontre algo")
    else:
        cerrarVentana_image_path = "images/cerrarVentana.png"

        cerrarVentana_image_location = pyautogui.locateCenterOnScreen(
            cerrarVentana_image_path, confidence=0.8
        )

        if cerrarVentana_image_location is not None:
            print(f"Imagen de cerrar ventana encontrada en {cerrarVentana_image_location}. Realizando clic...")
            pyautogui.click(cerrarVentana_image_location)
            print("Clic realizado en la imagen de cerrar ventana.")
        else:
            print("Imagen de cerrar ventana no encontrada en pantalla. Asegúrate de que sea visible.")

        print("Reiniciando ejecución de la función principal...")
        execute_ultra_bot()


    
    #! Se le da clic al panel desplegable de nuevo
    quinta_image_path = "images/panelDesplegableTest.png"
    quinta_image_location = pyautogui.locateCenterOnScreen(
        quinta_image_path, confidence=0.8)

    if quinta_image_location is not None:
        print(
            f"Quinta imagen encontrada en {quinta_image_location}. Realizando clic...")
        pyautogui.click(quinta_image_location)
        print("Clic realizado en la quinta imagen.")
    else:
        print("Quinta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(2)

    #! Se le da clic al boton de Me para abrir las opciones de usuario
    desplegable_me_image_path = "images/menuDesplegableMe.png"
    desplegable_me_image_location = pyautogui.locateCenterOnScreen(
        desplegable_me_image_path, confidence=0.8)

    if desplegable_me_image_location is not None:
        print(
            f"Quinta imagen encontrada en {desplegable_me_image_location}. Realizando clic...")
        pyautogui.click(desplegable_me_image_location)
        print("Clic realizado en la quinta imagen.")
    else:
        print("Quinta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(1)

    #! Se le da clic al boton de desloguear usuario
    signOut_image_path = "images/signOut.png"
    signOut_image_location = pyautogui.locateCenterOnScreen(
        signOut_image_path, confidence=0.8)

    if signOut_image_location is not None:
        print(
            f"Quinta imagen encontrada en {signOut_image_location}. Realizando clic...")
        pyautogui.click(signOut_image_location)
        print("Clic realizado en la quinta imagen.")
    else:
        print("Quinta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(3)

    #! Se le da clic al boton de desloguear usuario
    uneteAhora_image_path = "images/imagesTest/uneteAhoraTest.png"
    uneteAhora_image_location = pyautogui.locateCenterOnScreen(
        uneteAhora_image_path, confidence=0.8)

    if uneteAhora_image_location is not None:
        print(
            f"Quinta imagen encontrada en {uneteAhora_image_location}. Realizando clic...")
        pyautogui.click(uneteAhora_image_location)
        print("Clic realizado en la quinta imagen.")
    else:
        print("Quinta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(3)

    #! Se le da clic al boton de desloguear usuario
    iniciarSesionTest_image_path = "images/imagesTest/abc123.png"
    iniciarSesionTest_image_location = pyautogui.locateCenterOnScreen(
        iniciarSesionTest_image_path, confidence=0.8)

    if iniciarSesionTest_image_location is not None:
        print(
            f"Quinta imagen encontrada en {iniciarSesionTest_image_location}. Realizando clic...")
        pyautogui.click(iniciarSesionTest_image_location)
        print("Clic realizado en la quinta imagen.")
    else:
        print("Quinta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(4)

    #! Se le da clic al boton de desloguear usuario
    confirmarUsuarioTest_image_path = "images/imagesTest/confirmarUsuarioTest.png"
    confirmarUsuarioTest_image_location = pyautogui.locateCenterOnScreen(
        confirmarUsuarioTest_image_path, confidence=0.8)
    if confirmarUsuarioTest_image_location is not None:
        print(
            f"Sexta imagen encontrada en {confirmarUsuarioTest_image_location}. Preparando clic debajo...")

        offset_y = 120
        click_x = confirmarUsuarioTest_image_location[0]
        click_y = confirmarUsuarioTest_image_location[1] + offset_y

        pyautogui.click(click_x, click_y)
        print(
            f"Clic realizado debajo de la sexta imagen en ({click_x}, {click_y}).")
    else:
        print("Sexta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    time.sleep(7)

    #! Se le da clic al boton de desloguear usuario
    minimizarVentana_image_path = "images/minimizarVentana.png"
    minimizarVentana_image_location = pyautogui.locateCenterOnScreen(
        minimizarVentana_image_path, confidence=0.8)
    if minimizarVentana_image_location is not None:
        print(
            f"Sexta imagen encontrada en {minimizarVentana_image_location}. Preparando clic debajo...")

        pyautogui.click(minimizarVentana_image_location)
        print(
            f"Clic realizado debajo de la sexta imagen en ({minimizarVentana_image_location}).")
    else:
        print("Sexta imagen no encontrada en pantalla. Asegúrate de que sea visible.")

    print("Secuencia completada por el Ultra Bot.")
