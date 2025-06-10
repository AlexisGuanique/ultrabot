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
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

        max_attempts = 20  # 🔁 Aumentado a 20 intentos
        for attempt in range(1, max_attempts + 1):
            print(f"🔄 Intento {attempt} de {max_attempts}")

            try:
                # 🔍 Buscar contador de correos no leídos sin depender del texto
                inbox_elements = driver.find_elements(By.XPATH, "//a[span[contains(@class, 'unreadcount') and normalize-space(text()) != '']]")
                if inbox_elements:
                    print("📩 Se detectaron nuevos correos. Refrescando página...")
                    driver.refresh()
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
                    time.sleep(4)
                elif attempt % 3 == 0:
                    print("🔃 Refrescando página por iteración múltiplo de 3...")
                    driver.refresh()
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
                    time.sleep(4)
                else:
                    refresh_btn = driver.find_element(By.ID, "rcmbtn113")
                    refresh_btn.click()
                    time.sleep(2)

                unread_emails = driver.find_elements(By.CSS_SELECTOR, "tr.message.unread a")
                if not unread_emails:
                    print("🕐 No hay correos no leídos aún.")
                    time.sleep(5)
                    continue

                unread_emails[0].click()

                WebDriverWait(driver, 20).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "messagecontframe"))
                )
                time.sleep(1.5)

                try:
                    h1_code = driver.find_element(By.CSS_SELECTOR, "h1.v1sot-text-node-type--heading1 strong")
                    code = h1_code.text.strip()
                    if code:
                        pyperclip.copy(code)
                        print(f"📋 Código copiado desde <h1>: {code}")
                        return True
                except:
                    pass

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
                time.sleep(5)

    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    print("❌ No se pudo obtener el código de verificación tras múltiples intentos.")
    return False
