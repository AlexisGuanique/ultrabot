from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def openProfileWithExtraExtension():
    chromeOptions = Options()

    # ✅ Cargar perfil existente
    # Ruta dinámica al perfil de Chrome según el usuario de Windows
    user_profile = os.environ["USERPROFILE"]
    user_data_path = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data")

    chromeOptions.add_argument(f"--user-data-dir={user_data_path}")
    chromeOptions.add_argument("--profile-directory=Default")

    # Construir ruta completa a la extensión
    extension_path = os.path.join(
        user_profile,
        "AppData", "Local", "Google", "Chrome", "User Data",
        "Default", "Extensions",
        "hlkenndednhfkekhgcdicdfddnkalmdm",
        "1.13.0_0"
    )

    # Cargar la extensión
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
