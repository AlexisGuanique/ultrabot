from selenium.webdriver.common.by import By
# from ..database.database import get_hostinger_credentials 
from app.database.database import get_hostinger_credentials

from tkinter import messagebox
import time
import sys


def login_to_hostinger(driver):
    try:
        # 🔑 Obtener credenciales desde la base de datos
        creds = get_hostinger_credentials()
        if not creds:
            print("⚠️ No hay credenciales guardadas de Hostinger.")
            messagebox.showerror(
                "Credenciales de Hostinger faltantes",
                "Debes ingresar tu email y contraseña de Hostinger.\n\nHazlo desde la interfaz de configuración y vuelve a ejecutar la aplicación."
            )
            sys.exit()

        email = creds["email"]
        password = creds["password"]

        time.sleep(5)  # Esperar que cargue la página

        # Buscar los elementos
        user_input = driver.find_element(By.ID, "rcmloginuser")
        pass_input = driver.find_element(By.ID, "rcmloginpwd")
        login_button = driver.find_element(By.ID, "rcmloginsubmit")

        # Completar campos
        user_input.clear()
        user_input.send_keys(email)

        pass_input.clear()
        pass_input.send_keys(password)

        # Hacer clic en el botón
        login_button.click()

        print("✅ Login automático completado.")
    except Exception as e:
        print(f"❌ Error durante el login: {e}")
