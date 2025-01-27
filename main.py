from app.database.database import create_database
from app.ultrabot.ui import setup_ui


def main():
    # Crear la base de datos y tabla si no existen
    create_database()

    # Iniciar la interfaz gráfica
    setup_ui()

    # Ejecutar automatización (puedes activarlo desde la interfaz o descomentar para pruebas directas)
    # run_automation()

if __name__ == "__main__":
    main()
