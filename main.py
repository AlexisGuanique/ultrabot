import tkinter as tk
from tkinter import messagebox
from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.ui import setup_ui
from app.database.database import create_database, get_logged_in_user
from app.auth.auth import logout, verify_token


def on_login_success(login_data):
    create_database()

    name = login_data.get("name")
    lastname = login_data.get("lastname")

    if name and lastname:
        full_name = f"{name} {lastname}"
        # print(f"Bienvenido, {full_name}")
        setup_ui(full_name, on_login_success)
    else:
        print("Error: No se pudo obtener el nombre o apellido del usuario")


def main():
    create_database()

    # Consultar si hay un usuario logueado
    logged_in_user = get_logged_in_user()

    if logged_in_user:
        # Verificar el token antes de continuar
        # Si retorna None, asigna {"is_valid": False}
        token_status = verify_token() or {"is_valid": False}

        if not token_status.get("is_valid"):
            # Si el token es inválido o ha expirado, mostrar mensaje y forzar logout
            messagebox.showerror(
                "Token Expirado", "Usuario expirado. Contacte a los desarrolladores.")
            logout()
            setup_auth_ui(on_login_success)
            return

        # Si el token es válido, preguntar si quiere continuar logueado
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal temporalmente

        name = logged_in_user.get("name")
        lastname = logged_in_user.get("lastname")
        full_name = f"{name} {lastname}"

        result = messagebox.askyesno(
            "Usuario Logueado",
            f"El usuario {
                full_name} está actualmente logueado. ¿Deseas continuar logueado?"
        )

        if result:
            # print(f"Usuario {full_name} continúa logueado.")
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
