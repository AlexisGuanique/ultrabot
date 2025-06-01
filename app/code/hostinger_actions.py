from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import re
import time

def extract_code_from_text(text):
    match = re.search(r'\b\d{6}\b', text)
    return match.group(0) if match else None

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import re

def extract_code_from_text(text):
    match = re.search(r'\b\d{6}\b', text)
    return match.group(0) if match else None

def perform_hostinger_actions(driver):
    try:
        wait = WebDriverWait(driver, 30)

        # Asegurar que la tabla de correos esté presente
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

        max_attempts = 10
        for attempt in range(1, max_attempts + 1):
            print(f"🔄 Intento {attempt} de {max_attempts}")

            try:
                # Hacer clic en el botón de "Actualizar"
                refresh_btn = driver.find_element(By.ID, "rcmbtn113")
                refresh_btn.click()
                time.sleep(2)

                # Buscar todos los correos no leídos
                unread_emails = driver.find_elements(By.CSS_SELECTOR, "tr.message.unread a")

                if not unread_emails:
                    print("🕐 No hay correos no leídos aún.")
                    time.sleep(3)
                    continue

                # Hacer clic en el primer correo no leído (el más reciente arriba)
                unread_emails[0].click()

                # Esperar el iframe del contenido y cambiar el foco
                WebDriverWait(driver, 20).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "messagecontframe"))
                )
                time.sleep(1.5)

                # Buscar en <h1>
                try:
                    h1_code = driver.find_element(By.CSS_SELECTOR, "h1.v1sot-text-node-type--heading1 strong")
                    code = h1_code.text.strip()
                    if code:
                        pyperclip.copy(code)
                        print(f"📋 Código copiado desde <h1>: {code}")
                        return True
                except:
                    pass

                # Buscar en <h2>
                try:
                    h2 = driver.find_element(By.CSS_SELECTOR, "h2.subject")
                    text = h2.text.strip()
                    code = extract_code_from_text(text)
                    if code:
                        pyperclip.copy(code)
                        print(f"📋 Código copiado desde <h2>: {code}")
                        return True
                except:
                    pass

                driver.switch_to.default_content()

            except Exception as e:
                print(f"⚠️ Error en intento {attempt}: {e}")
                driver.switch_to.default_content()
                time.sleep(3)

    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    print("❌ No se pudo obtener el código de verificación tras múltiples intentos.")
    return False
