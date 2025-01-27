import tkinter as tk
from tkinter import messagebox
from app.auth.auth import login


def setup_auth_ui(on_login_success):
    """
    Configura la interfaz gráfica de autenticación.
    :param on_login_success: Callback para manejar el login exitoso.
    """
    def handle_login():
        """Maneja el evento de inicio de sesión."""
        username = username_entry.get()
        password = password_entry.get()

        if login(username, password):
            messagebox.showinfo("Login Exitoso", f"Bienvenido, {username}!")
            root.destroy()  # Cerrar la ventana de login
            on_login_success(username)  # Llamar al callback de login exitoso
        else:
            messagebox.showerror(
                "Login Fallido", "Usuario o contraseña incorrectos.")

    # Ventana de login
    root = tk.Tk()
    root.title("Login - Ultra Bot")
    root.geometry("400x300")

    # Etiqueta y entrada de usuario
    username_label = tk.Label(root, text="Usuario:", font=("Arial", 12))
    username_label.pack(pady=10)
    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.pack(pady=5)

    # Etiqueta y entrada de contraseña
    password_label = tk.Label(root, text="Contraseña:", font=("Arial", 12))
    password_label.pack(pady=10)
    password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    # Botón de login
    login_button = tk.Button(root, text="Iniciar Sesión", command=handle_login, font=(
        "Arial", 12), bg="green", fg="white")
    login_button.pack(pady=20)

    # Ejecutar el bucle principal
    root.mainloop()
