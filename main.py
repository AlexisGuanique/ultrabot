from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.ui import setup_ui
from app.database.database import create_database

def on_login_success(username):
    """
    Callback para manejar el éxito del login.
    :param username: Usuario logueado.
    """
    create_database()  # Crear la base de datos si no existe

    print("Base de datos creada con éxito.")
    print(f"Usuario logueado: {username}")
    setup_ui(username, on_login_success)  # Pasamos la función como referencia

def main():
    # Mostrar la ventana de login
    setup_auth_ui(on_login_success)

if __name__ == "__main__":
    main()
