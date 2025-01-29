import tkinter as tk
from tkinter import messagebox
from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.ui import setup_ui
from app.database.database import create_database
from app.database.database import get_logged_in_user
from app.auth.auth import logout


def on_login_success(login_data):

    create_database()


    name = login_data.get("name")
    lastname = login_data.get("lastname")
    
    if name and lastname:
        full_name = f"{name} {lastname}"
        print(f"Bienvenido, {full_name}")
        setup_ui(full_name, on_login_success)
    else:
        print("Error: No se pudo obtener el nombre o apellido del usuario")


def main():

    create_database()

    # Consultar si hay un usuario logueado
    logged_in_user = get_logged_in_user()

    if logged_in_user:
        # Si hay un usuario logueado, mostrar un cuadro de diálogo
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal temporalmente

        name = logged_in_user.get("name")
        lastname = logged_in_user.get("lastname")
        full_name = f"{name} {lastname}"

        result = messagebox.askyesno(
            "Usuario Logueado",
            f"El usuario {full_name} está actualmente logueado. ¿Deseas continuar logueado?"
        )

        if result:
            # Si el usuario desea continuar logueado
            print(f"Usuario {full_name} continúa logueado.")
            root.destroy()
            setup_ui(full_name, on_login_success)
        else:
            # Si el usuario no desea continuar logueado
            logout()
            messagebox.showinfo("Logout Exitoso", "Has cerrado sesión.")
            root.destroy()
            setup_auth_ui(on_login_success)
    else:
        # Si no hay un usuario logueado, mostrar la pantalla de login
        setup_auth_ui(on_login_success)


if __name__ == "__main__":
    main()
