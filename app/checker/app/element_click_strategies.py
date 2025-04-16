from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui


def click_next(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='Next']"))
        )
        print("🔍 Botón 'Next' detectado. Redireccionando...")

        driver.get("https://www.linkedin.com/feed/")
        print("🌐 Navegado a: https://www.linkedin.com/feed/")
        return True

    except:
        print("✅ Botón 'Next' no está presente.")
        return False


def click_feed_refresh_and_logout(driver):
    try:
        # Paso 1: Verificar que estamos en el feed (ícono de LinkedIn visible)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "li-icon[type='app-linkedin-bug-color-icon']")
            )
        )
        print("✅ Ícono de LinkedIn detectado en el feed.")

      # Paso 2: Clic en el botón del menú "Yo"
        menu_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.global-nav__primary-link-me-menu-trigger")
            )
        )
        menu_button.click()
        print("👤 Se hizo clic en el botón de menú 'Yo'.")

        # Paso 2.1: Esperar que el menú realmente se muestre en el DOM
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    # menú desplegado
                    (By.CSS_SELECTOR,
                     "div.global-nav__me-content[aria-hidden='false']")
                )
            )
            print("📂 Menú desplegable visible. Procediendo con TABs...")
        except Exception as e:
            print("❌ El menú desplegable no se mostró a tiempo:", e)
            return False  # no seguimos si no aparece el menú

        # Paso 3: Simular TABs y ENTER para cerrar sesión
        for i in range(9):
            pyautogui.press('tab')
            print(f"🟩 TAB {i+1} enviado")
            time.sleep(1)

        pyautogui.press('enter')
        print("🔒 Se simuló ENTER después de 9 TABs.")


        pyautogui.press('enter')
        print("🔒 Se simuló ENTER después de 9 TABs.")

        time.sleep(2)  # Esperar a que se procese el logout

        # Paso 4: Verificar si fue redirigido al login (verificación post logout)
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[data-test-id='home-hero-sign-in-cta']"))
            )
            print("⚠️ Botón 'Sign in with email' detectado. Abortando cookie...")
            return False
        except:
            pass

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.remember-me-sign-in-cta"))
            )
            print("⚠️ Botón 'Sign in as' detectado. Abortando cookie...")
            return False
        except:
            pass

        return True

    except Exception as e:
        print("❌ No se pudo realizar el flujo de logout:", e)
        return False


def should_abort_session(driver):
    # Detecta "Sign in with email"
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-test-id='home-hero-sign-in-cta']"))
        )
        print("⚠️ Botón 'Sign in with email' detectado. Abortando cookie...")
        return True
    except:
        pass

    # Detecta "Sign in as"
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.remember-me-sign-in-cta"))
        )
        print("⚠️ Botón 'Sign in as' detectado. Abortando cookie...")
        return True
    except:
        pass

    # Detecta "More actions"
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "more_actions_btn_0"))
        )
        print("⚠️ Botón 'More actions' detectado. Abortando cookie...")
        return True
    except:
        pass

    # Detecta input de contraseña
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        print("⚠️ Input de contraseña detectado. Abortando cookie...")
        return True
    except:
        pass

    return False
