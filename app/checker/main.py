# main.py
from app.profile_opener import openProfile  # Asegúrate de tener este módulo configurado correctamente
from app.extension_opener import openExtensionWithImageClick
import time

def main():
    # 1. Abrir Chrome con Selenium usando tu perfil
    driver = openProfile()
    
    # 2. Navegar a la página donde se mostrará la extensión (por ejemplo, la página de registro de LinkedIn)
   #  driver.get("https://www.linkedin.com/signup?trk=guest_homepage-basic_nav-header-join")
    driver.get("https://www.linkedin.com/")

    time.sleep(224234)  # Espera a que la página cargue completamente
    

    openExtensionWithImageClick(driver, imagePath="cookie.png", confidenceLevel=0.8)
    
    # 4. Mantener la ventana abierta para revisión
    input("Presiona Enter para cerrar el navegador...")
    driver.quit()

if __name__ == "__main__":
    main()
