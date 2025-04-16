import tkinter as tk
from tkinter import messagebox
from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.ui import setup_ui
from app.database.database import create_database, get_logged_in_user
from app.auth.auth import logout, verify_token
from choice_dialog import choice_dialog
from app.checker.app.ui.checker_ui import setup_checker_ui

def on_login_success(login_data):
    # Crear o verificar la base de datos
    create_database()

    name = login_data.get("name")
    lastname = login_data.get("lastname")

    if name and lastname:
        full_name = f"{name} {lastname}"
        # Crear la ventana principal oculta para que aparezca el diálogo
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana raíz

        # Mostrar el diálogo de elección
        choice = choice_dialog(
            "Login Exitoso",
            f"Bienvenido, {full_name}!\n\n¿A dónde quieres ir?"
        )

        root.destroy()

        if choice == "UltraBot":
            # Ir a la interfaz UltraBot
            setup_ui(full_name, on_login_success)
        elif choice == "Checker":
            # Por el momento, se muestra un mensaje informativo
            setup_checker_ui(full_name, on_login_success)
        else:
            messagebox.showwarning(
                "Sin selección", "No se seleccionó ninguna opción.")
    else:
        print("Error: No se pudo obtener el nombre o apellido del usuario")


def main():
    create_database()

    logged_in_user = get_logged_in_user()

    if logged_in_user:
        token_status = verify_token() or {"is_valid": False}
        if not token_status.get("is_valid"):
            messagebox.showerror(
                "Token Expirado", "Usuario expirado. Contacte a los desarrolladores.")
            logout()
            setup_auth_ui(on_login_success)
            return

        # Crear ventana oculta para los messagebox
        root = tk.Tk()
        root.withdraw()

        name = logged_in_user.get("name")
        lastname = logged_in_user.get("lastname")
        full_name = f"{name} {lastname}"

        # Mostrar el diálogo personalizado para elegir entre UltraBot y Checker.
        user_choice = choice_dialog(
            "Usuario Logueado",
            f"Hola {full_name} estás actualmente logueado.\n\n¿A dónde quieres ir?"
        )
        root.destroy()

        if user_choice == "UltraBot":
            setup_ui(full_name, on_login_success)
        elif user_choice == "Checker":
            # Por el momento, se muestra un mensaje informativo
            setup_checker_ui(full_name, on_login_success)
        else:
            logout()
            messagebox.showinfo("Logout", "Has cerrado sesión.")
            setup_auth_ui(on_login_success)
    else:
        setup_auth_ui(on_login_success)


if __name__ == "__main__":
    main()
