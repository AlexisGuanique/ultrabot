from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def click_next(driver):

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']"))
        )
        element.click()
        print("Se hizo clic en el botón 'Next'.")
        return True
    except Exception as e:
        print("Botón 'Next' no encontrado:", e)
        return False

def click_feed_refresh(driver):

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-test-app-aware-link][href*='doFeedRefresh=true']"))
        )
        element.click()
        print("Se hizo clic en el enlace de feed refresh.")
        return True
    except Exception as e:
        print("Enlace de feed refresh no encontrado:", e)
        return False

def click_remember_me(driver):

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-test-id='home-hero-sign-in-cta']")
            )
        )
        element.click()
        print("Se hizo clic en 'Sign in with email' mediante data-test-id.")
        
    except Exception as e:
        print("Botón 'Sign in with email' no encontrado:", e)
        # Continúa con el siguiente proceso

    time.sleep(1)  # Espera breve para que se actualice la interfaz

    # Paso 1: Dar clic en "Sign in as"
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.remember-me-sign-in-cta"))
        )
        element.click()
        print("Se hizo clic en 'Sign in as' (remember-me-sign-in-cta) con Selenium.")
    except Exception as e:
        print("Error interactuando con el botón 'remember-me-sign-in-cta':", e)

    time.sleep(2)  # Espera para que se actualice la interfaz

    # Paso 2: Dar clic en "More actions"
    try:
        more_actions_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "more_actions_btn_0"))
        )
        more_actions_button.click()
        print("Se hizo clic en 'More actions' (id: more_actions_btn_0) con Selenium.")
    except Exception as e:
        print("Error interactuando con el botón 'more_actions_btn_0':", e)
    
    time.sleep(1)  # Espera para que se despliegue el dropdown

    # Paso 3: Dar clic en "Forget this account"
    try:
        forget_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "forget-account-btn_0"))
        )
        forget_button.click()
        print("Se hizo clic en 'Forget this account' (id: forget-account-btn_0) con Selenium.")
    except Exception as e:
        print("Error al hacer clic en 'Forget this account':", e)
    
    time.sleep(1)  # Espera antes de pasar al input de contraseña

    # Paso 4: Ingresar la contraseña en el input (id "password")
    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_input.clear()
        password = "5zhL5V21gN6b9e7"  # Ajusta la contraseña según necesites
        password_input.send_keys(password)
        print("Se pegó la contraseña en el input 'password'.")
    except Exception as e:
        print("Error al llenar el input de contraseña:", e)
    
    time.sleep(1)

    # Paso 5: Dar clic en el botón "Sign in"
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-litms-control-urn='login-submit']"))
        )
        sign_in_button.click()
        print("Se hizo clic en 'Sign in'.")
    except Exception as e:
        print("Error al hacer clic en el botón 'Sign in':", e)

    return True
