from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def openProfileWithExtraExtension():
    chromeOptions = Options()

    # Modo incógnito
    chromeOptions.add_argument("--incognito")

    # Cargar perfil existente
    chromeOptions.add_argument(
        r"--user-data-dir=C:/Users/Usuario/AppData/Local/Google/Chrome/User Data")
    chromeOptions.add_argument("--profile-directory=Profile 5")

    # Cargar extensión manualmente desde carpeta
    extension_path = r"C:/Users/Usuario/AppData/Local/Google/Chrome/User Data/Profile 5/Extensions/hlkenndednhfkekhgcdicdfddnkalmdm/1.13.0_0"
    chromeOptions.add_argument(f"--load-extension={extension_path}")

    # Mantener ventana abierta
    chromeOptions.add_experimental_option("detach", True)

    # Prevenir problemas
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("--disable-software-rasterizer")

    # Opcional: evitar detección de automatización (algunos efectos secundarios)
    chromeOptions.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chromeOptions)
    return driver
