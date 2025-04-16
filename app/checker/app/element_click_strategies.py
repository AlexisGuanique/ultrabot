from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def click_next(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']"))
        )
        print("🔍 Botón 'Next' detectado. Redireccionando...")

        driver.get("https://www.linkedin.com/feed/")
        print("🌐 Navegado a: https://www.linkedin.com/feed/")
        return True

    except:
        print("✅ Botón 'Next' no está presente.")
        return False



def click_feed_refresh(driver):

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-test-app-aware-link][href*='doFeedRefresh=true']"))
        )
        element.click()
        print("Se hizo clic en el enlace de feed refresh.")
        return True
    except Exception as e:
        print("Enlace de feed refresh no encontrado:", e)
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
