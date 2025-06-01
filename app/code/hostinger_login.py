# hostinger_login.py

from selenium.webdriver.common.by import By
import time

def login_to_hostinger(driver):
    try:
        time.sleep(5)  # Esperar que cargue la página

        # Buscar los elementos
        user_input = driver.find_element(By.ID, "rcmloginuser")
        pass_input = driver.find_element(By.ID, "rcmloginpwd")
        login_button = driver.find_element(By.ID, "rcmloginsubmit")

        # Completar campos
        user_input.clear()
        user_input.send_keys("Gemmanic@valdegembarca.com ")

        pass_input.clear()
        pass_input.send_keys("s:=aaO8>wU")

        # Hacer clic en el botón
        login_button.click()

        print("✅ Login automático completado.")
    except Exception as e:
        print(f"❌ Error durante el login: {e}")
