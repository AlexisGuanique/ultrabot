from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from hostinger_login import login_to_hostinger

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

        print("✅ Página abierta. Presiona Enter aquí para cerrar la ventana manualmente.")
        input("⏳ Esperando... ")
        # driver.quit()  # ← si querés cerrar luego de presionar Enter
    except Exception as e:
        print(f"❌ Error al abrir Chrome: {e}")

if __name__ == "__main__":
    run_checker()


