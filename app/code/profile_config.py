from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from hostinger_login import login_to_hostinger
# from hostinger_actions import perform_hostinger_actions
import time

import sys
import os

# Agrega la raíz del proyecto al sys.path para poder importar 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.code.hostinger_login import login_to_hostinger

from app.code.hostinger_actions import perform_hostinger_actions


def open_temp_chrome_profile():
    chrome_options = Options()

    # Crear un perfil temporal (no requiere que cierres el Chrome real)
    chrome_options.add_argument("--user-data-dir=C:/temp/selenium-profile")
    chrome_options.add_argument("--profile-directory=Profile 1")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    return driver



def run_checker():
    print("🟢 Abriendo Chrome con perfil temporal...")
    try:
        driver = open_temp_chrome_profile()
        driver.get("https://mail.hostinger.com/?_task=mail&_mbox=INBOX")

        login_to_hostinger(driver)

        time.sleep(4)

        success = perform_hostinger_actions(driver)

        if success:
            print("✅ Código copiado. Cerrando Chrome automáticamente...")
        else:
            print("⚠️ Código no encontrado. Cerrando Chrome igualmente...")

        driver.quit()

    except Exception as e:
        print(f"❌ Error al abrir Chrome: {e}")





if __name__ == "__main__":
    run_checker()


