import tkinter as tk
from tkinter import filedialog, messagebox
from app.database.database import save_cookies_to_db, clear_database, create_database, get_cookie_count
from app.ultrabot.file_handler import read_cookies_from_txt
from app.ultrabot.ultra_bot import execute_ultra_bot
from app.auth.auth import logout


def setup_ui(logged_in_user, on_login_success):
    """
    Configura la interfaz gráfica principal después del login.
    :param logged_in_user: Nombre de usuario logueado.
    :param on_login_success: Callback para regresar al login.
    """
    def process_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Seleccionar archivo de texto"
        )
        if file_path:
            cookies = read_cookies_from_txt(file_path)
            if cookies:
                create_database()
                save_cookies_to_db(cookies)
                update_cookie_count()
                messagebox.showinfo("Éxito", f"Se guardaron {len(cookies)} cookies en la base de datos.")
            else:
                messagebox.showerror("Error", "No se pudieron leer cookies del archivo.")

    def update_cookie_count():
        """Actualiza el contador de cookies en la base de datos."""
        total_cookies = get_cookie_count()
        file_label.config(text=f"Total de cookies en la base de datos: {total_cookies}")

    def clear_db():
        try:
            clear_database()
            update_cookie_count()
            messagebox.showinfo("Base de Datos Limpiada", "Todos los registros fueron eliminados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error al Limpiar", f"Se produjo un error al limpiar la base de datos:\n{e}")

    def handle_logout():
        """Maneja el cierre de sesión."""
        if logout():
            messagebox.showinfo("Logout Exitoso", "Has cerrado sesión.")
            root.destroy()  # Cierra la ventana principal para regresar al login
            from app.ultrabot.auth_ui import setup_auth_ui
            setup_auth_ui(on_login_success)  # Usa la referencia pasada desde main.py

    # Ventana principal
    root = tk.Tk()
    root.title("Ultra Bot")
    root.geometry("1000x600")

    # Etiqueta de bienvenida
    welcome_label = tk.Label(root, text=f"Bienvenido, {logged_in_user}", font=("Arial", 16))
    welcome_label.pack(pady=20)

    # Contador de cookies
    file_label = tk.Label(root, text="Total de cookies en la base de datos: 0", wraplength=500)
    file_label.pack(pady=10)
    update_cookie_count()

    # Botones principales
    process_button = tk.Button(root, text="Cargar Cookies", command=process_file, font=("Arial", 12))
    process_button.pack(pady=10)

    ultra_bot_button = tk.Button(root, text="Ejecutar Ultra Bot", command=execute_ultra_bot, font=("Arial", 12), bg="green", fg="white")
    ultra_bot_button.pack(pady=10)

    clear_db_button = tk.Button(root, text="Limpiar Base de Datos", command=clear_db, font=("Arial", 12), bg="red", fg="white")
    clear_db_button.pack(pady=10)

    # Botón de logout
    logout_button = tk.Button(root, text="Cerrar Sesión", command=handle_logout, font=("Arial", 12), bg="orange", fg="white")
    logout_button.pack(pady=10)

    # Ejecutar el bucle principal
    root.mainloop()
