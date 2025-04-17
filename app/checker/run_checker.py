import sys
import time
from tkinter import messagebox
from .app.profile_opener import openProfileWithExtraExtension
from .app.extension_opener import openExtensionWithImageClick
from ..database.database import get_account_cookie_by_id, count_account_cookies


def run_checker():
    total_cookies = count_account_cookies()

    for cookie_id in range(1, total_cookies + 1):
        print(f"🔁 Ejecutando checker con cookie ID: {cookie_id}")

        # 1. Obtener la cookie correspondiente
        cookie = get_account_cookie_by_id(cookie_id)
        if not cookie:
            print(f"⚠️ Cookie con ID {cookie_id} no encontrada. Saltando...")
            continue

        # 2. Abrir Chrome con perfil y extensión
        driver = openProfileWithExtraExtension()
        driver.get("https://www.linkedin.com/")
        time.sleep(0.5)

        # 3. Ejecutar el flujo del checker con esa cookie
        try:
            openExtensionWithImageClick(
                driver,
                imagePath="cookie.png",
                confidenceLevel=0.8,
                override_cookie=cookie
            )
        except Exception as e:
            print(f"❌ Error al correr checker con cookie ID {cookie_id}: {e}")
        finally:
            driver.quit()

        time.sleep(0.5)

    # 🔚 Cuando se terminan las cookies:
    print("✅ Cookies chequeadas con éxito.")
    messagebox.showinfo(
            "Ultra Checker finalizado",
            "Checker detenido por falta de cookies"
        )
    sys.exit()
