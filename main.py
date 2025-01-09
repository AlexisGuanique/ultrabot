from database import create_database
from ui import setup_ui

def main():
    # Crear la base de datos y tabla si no existen
    create_database()

    # Iniciar la interfaz gráfica
    setup_ui()

if __name__ == "__main__":
    main()
