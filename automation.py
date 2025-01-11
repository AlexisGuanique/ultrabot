import pyautogui
import subprocess
import time
import sqlite3

def open_program():
    """Abre la aplicación Ultra desde su ruta específica."""
    program_path = r"C:\Users\Usuario\AppData\Local\Programs\Ultra\Ultra.exe"
    try:
        subprocess.Popen([program_path])
        print(f"Programa {program_path} abierto exitosamente.")
        time.sleep(5)  # Esperar a que el programa cargue
    except Exception as e:
        print(f"Error al abrir el programa: {e}")

def find_and_click_button():
    """Encuentra un botón en la pantalla y hace clic en él."""
    button_image_path = r"C:\Users\Usuario\workspace\ultra\ultrabot\images\ingresar-cookies.png"
    try:
        button_location = pyautogui.locateOnScreen(button_image_path, confidence=0.8)
        if button_location:
            pyautogui.click(button_location)
            print(f"Botón encontrado y clickeado en: {button_location}")
        else:
            print("No se encontró el botón en la pantalla.")
    except Exception as e:
        print(f"Error al buscar o hacer clic en el botón: {e}")

def type_in_input_field(cookie_text):
    """Escribe o pega texto en el campo de entrada."""
    try:
        pyautogui.write(cookie_text, interval=0.1)
        print("Texto escrito en el campo de entrada.")
    except Exception as e:
        print(f"Error al escribir en el campo de entrada: {e}")

def get_cookie_from_db():
    """Obtiene una cookie desde la base de datos."""
    try:
        conn = sqlite3.connect('cookies.db')
        cursor = conn.cursor()

        cursor.execute("SELECT cookie FROM cookies LIMIT 1")  # Recuperar la primera cookie
        row = cursor.fetchone()

        conn.close()

        if row:
            return row[0]
        else:
            print("No hay cookies en la base de datos.")
            return None
    except Exception as e:
        print(f"Error al recuperar la cookie: {e}")
        return None
