from database import create_database
from ui import setup_ui
from automation import open_program, find_and_click_button, get_cookie_from_db, type_in_input_field

def run_automation():
    """Ejecuta acciones automatizadas en la aplicación Ultra."""
    # Abrir la aplicación Ultra
    open_program()

    # Buscar y hacer clic en el botón
    find_and_click_button()

    # Recuperar una cookie de la base de datos
    cookie = get_cookie_from_db()
    if cookie:
        # Escribir la cookie en el campo de entrada
        type_in_input_field(cookie)

def main():
    # Crear la base de datos y tabla si no existen
    create_database()

    # Iniciar la interfaz gráfica
    setup_ui()

    # Ejecutar automatización (puedes activarlo desde la interfaz o descomentar para pruebas directas)
    # run_automation()

if __name__ == "__main__":
    main()
