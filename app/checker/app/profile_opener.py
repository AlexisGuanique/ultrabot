from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def openProfileWithExtraExtension():
    chromeOptions = Options()

    # ✅ Cargar perfil existente
    chromeOptions.add_argument(
        r"--user-data-dir=C:/Users/Usuario/AppData/Local/Google/Chrome/User Data"
    )
    chromeOptions.add_argument("--profile-directory=Default")

    # ✅ Cargar extensión manualmente desde carpeta
    extension_path = r"C:/Users/Usuario/AppData/Local/Google/Chrome/User Data/Profile 5/Extensions/hlkenndednhfkekhgcdicdfddnkalmdm/1.13.0_0"
    chromeOptions.add_argument(f"--load-extension={extension_path}")

    # ⚙️ Optimizar rendimiento y evitar errores de GPU
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("--disable-software-rasterizer")
    chromeOptions.add_argument("--disable-features=VizDisplayCompositor")
    chromeOptions.add_argument("--disable-accelerated-2d-canvas")
    chromeOptions.add_argument("--disable-accelerated-video-decode")
    chromeOptions.add_argument("--disable-accelerated-mjpeg-decode")

    # ❌ No usar headless si cargas extensiones
    # chromeOptions.add_argument("--headless=new")  ← No compatible

    # 🕵️ Opcional: evitar detección de Selenium
    chromeOptions.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option("useAutomationExtension", False)

    # Crear driver
    driver = webdriver.Chrome(options=chromeOptions)
    return driver
