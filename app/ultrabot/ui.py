import tkinter as tk
from tkinter import filedialog, messagebox
from app.database.database import save_cookies_to_db, clear_database, create_database, get_cookie_count
from app.ultrabot.file_handler import read_cookies_from_txt
from app.ultrabot.ultra_bot import execute_ultra_bot, stop_ultra_bot
from app.auth.auth import verify_token, logout
from app.ultrabot.auth_ui import setup_auth_ui


def setup_ui(logged_in_user, on_login_success):
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
                messagebox.showinfo(
                    "Éxito", f"Se guardaron {len(cookies)} cookies en la base de datos.")
            else:
                messagebox.showerror(
                    "Error", "No se pudieron leer cookies del archivo.")

    def update_cookie_count():
        """Actualiza el contador de cookies en la base de datos."""
        total_cookies = get_cookie_count()
        file_label.config(
            text=f"Total de cookies en la base de datos: {total_cookies}")

    def clear_db():
        try:
            clear_database()
            update_cookie_count()
            messagebox.showinfo(
                "Base de Datos Limpiada", "Todos los registros fueron eliminados exitosamente.")
        except Exception as e:
            messagebox.showerror(
                "Error al Limpiar", f"Se produjo un error al limpiar la base de datos:\n{e}")

    def handle_logout():

        from app.ultrabot.auth_ui import setup_auth_ui

        if logout():
            messagebox.showinfo("Logout Exitoso", "Has cerrado sesión.")
            root.destroy()  # Cierra la ventana actual
            setup_auth_ui(on_login_success)  # Muestra la pantalla de login
        else:
            messagebox.showwarning("Error", "No hay ningún usuario logueado.")

    def handle_ultra_bot():
        """Verifica el token antes de ejecutar el Ultra Bot."""
        token_data = verify_token()
        if not (token_data and token_data.get("is_valid")):
            messagebox.showerror(
                "Usuario expirado", "Usuario expirado, por favor contacte con los desarrolladores.")
            logout()
            root.destroy()
            setup_auth_ui(on_login_success)
            return

        execute_ultra_bot()  # Iniciar el bot

    def handle_stop_ultra_bot():
        """Detiene la ejecución del Ultra Bot."""
        stop_ultra_bot()
        print("🛑 Bot detenido desde la UI.")

    # Ventana principal
    root = tk.Tk()
    root.title("Ultra Bot")
    root.geometry("1000x600")

    # Etiqueta de bienvenida
    welcome_label = tk.Label(
        root, text=f"Bienvenido, {logged_in_user}", font=("Arial", 16))
    welcome_label.pack(pady=20)

    # Contador de cookies
    file_label = tk.Label(
        root, text="Total de cookies en la base de datos: 0", wraplength=500)
    file_label.pack(pady=10)
    update_cookie_count()

    # Botones principales
    process_button = tk.Button(
        root, text="Cargar Cookies", command=process_file, font=("Arial", 12))
    process_button.pack(pady=10)

    # Botón para iniciar el bot
    ultra_bot_button = tk.Button(root, text="Ejecutar Ultra Bot", command=handle_ultra_bot, font=(
        "Arial", 12), bg="green", fg="white")
    ultra_bot_button.pack(pady=10)

    # Botón para detener el bot
    stop_bot_button = tk.Button(root, text="Detener Ultra Bot", command=handle_stop_ultra_bot, font=(
        "Arial", 12), bg="red", fg="white")
    stop_bot_button.pack(pady=10)

    clear_db_button = tk.Button(root, text="Limpiar Base de Datos", command=clear_db, font=(
        "Arial", 12), bg="red", fg="white")
    clear_db_button.pack(pady=10)

    # Botón de logout
    logout_button = tk.Button(root, text="Cerrar Sesión", command=handle_logout, font=(
        "Arial", 12), bg="orange", fg="white")
    logout_button.pack(pady=10)

    # Ejecutar el bucle principal
    root.mainloop()
