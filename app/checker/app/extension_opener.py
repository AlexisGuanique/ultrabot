import time
import pyautogui
import pyperclip
from app.utils.file_reader import read_text_from_file
import app.element_click_strategies as ecs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def openExtensionWithImageClick(driver, imagePath="cookie.png", confidenceLevel=0.8):

    try:
        extension_icon_x, extension_icon_y = 1218, 90  # Ajusta según tu pantalla
        pyautogui.moveTo(extension_icon_x, extension_icon_y, duration=0.3)
        pyautogui.rightClick()
        print(f"Right-clicked extension icon at: ({extension_icon_x}, {extension_icon_y})")
    except Exception as e:
        print(f"Error right-clicking extension icon: {e}")
    
    time.sleep(1)  # Espera a que se despliegue el popup de la extensión
    
    # Paso 2: Clic izquierdo en la posición determinada.
    try:
        x2, y2 = 1121, 324  # Coordenadas para el clic izquierdo
        pyautogui.moveTo(x2, y2, duration=0.3)
        pyautogui.click()
        print(f"Left-clicked at: ({x2}, {y2})")
    except Exception as e:
        print(f"Error left-clicking at: {e}")
    
    # Paso 3: Leer el contenido desde "cookie.txt".
    text_content = read_text_from_file("cookie.txt")
    print("Texto leído:", text_content)
    

    time.sleep(1)  # Espera para que se muestre el input del popup.
    # Paso 4: Clic en el botón 'Import'.
    try:
        button_x, button_y = 1298, 811  # Coordenadas del botón "Import" (ajusta según tu pantalla)
        pyautogui.moveTo(button_x, button_y, duration=0.3)
        pyautogui.click()
        print(f"Clicked 'Import' button at: ({button_x}, {button_y})")
    except Exception as e:
        print(f"Error clicking 'Import' button: {e}")
        
    time.sleep(1)  # Espera para que se muestre el input del popup.
    
    # Paso 4.1: Copiar y pegar el contenido usando hotkey.
    try:
        pyperclip.copy(text_content)
        pyautogui.hotkey("command", "v")
        print("Texto pegado mediante hotkey (Command+V).")
    except Exception as e:
        print(f"Error al pegar el texto: {e}")
    
    time.sleep(1)
    
    # Paso 5: Clic final en la posición deseada (solo clic, sin pegado).
    try:
        final_click_x, final_click_y = 1332, 812  # Ajusta según necesites
        pyautogui.moveTo(final_click_x, final_click_y, duration=0.3)
        pyautogui.click()
        print(f"Final click at: ({final_click_x}, {final_click_y})")
    except Exception as e:
        print(f"Error en el clic final: {e}")
    
    time.sleep(1)
    
    # Paso 6: Refrescar la ventana usando Selenium.
    try:
        driver.refresh()
        print("La ventana se ha refrescado.")
    except Exception as e:
        print(f"Error al refrescar la ventana: {e}")
    
    time.sleep(6)
    
    # Paso 7: Intentar localizar y dar clic a uno de varios elementos posibles.
    # Se ejecutan cada uno de los procesos definidos en element_click_strategies.py.
    # Se intentan en secuencia hasta que uno retorne True.
    process_clicked = (
        ecs.click_remember_me(driver)
        or  ecs.click_next(driver)
        or ecs.click_feed_refresh(driver)
    )
    
    if not process_clicked:
        print("Ninguno de los elementos se encontró para dar clic.")

    # Paso 8: Último clic en las coordenadas (1381, 812), luego guarda lo que se copia en el portapapeles en un .txt.
    time.sleep(1)
    try:
        last_click_x, last_click_y = 1381, 812  # Coordenadas del último clic
        pyautogui.moveTo(last_click_x, last_click_y, duration=0.3)
        pyautogui.click()  # Clic izquierdo
        print(f"Last click at: ({last_click_x}, {last_click_y})")
    except Exception as e:
        print(f"Error en el último clic: {e}")
    
    time.sleep(1)  # Espera a que algo se copie al portapapeles
    try:
        clipboard_content = pyperclip.paste()
        with open("clipboard_output.txt", "w", encoding="utf-8") as f:
            f.write(clipboard_content)
        print("Contenido del portapapeles guardado en 'clipboard_output.txt'.")
    except Exception as e:
        print(f"Error al guardar el contenido del portapapeles: {e}")
