import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from app.database.database import save_cookies_to_db, clear_database, create_database, get_cookie_count, save_bot_settings, get_bot_settings
from app.ultrabot.file_handler import read_cookies_from_txt
from app.ultrabot.ultra_bot import execute_ultra_bot, stop_ultra_bot
from app.auth.auth import verify_token, logout
from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder


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
        file_label.configure(
            text=f"Total de cookies en la base de datos: {total_cookies}")

    def clear_db():
        """Muestra una caja de confirmación antes de limpiar la base de datos."""
        confirm = messagebox.askyesno(
            "Confirmar acción", "¿Seguro que quieres limpiar las Cookies?"
        )

        if confirm:  # Si el usuario hace clic en "Sí"
            try:
                clear_database()
                update_cookie_count()
                messagebox.showinfo(
                    "Cookies Limpiadas", "Todas las cookies fueron eliminadas exitosamente."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error al Limpiar", f"Se produjo un error al limpiar la base de datos:\n{e}"
                )
        else:
            # Mensaje opcional
            messagebox.showinfo("Acción cancelada",
                                "No se han eliminado las Cookies.")

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
        """Detiene la ejecución del Ultra Bot y muestra un mensaje de confirmación."""
        stop_ultra_bot()
        print("🛑 Bot detenido desde la UI.")
        messagebox.showinfo("Ultra Bot", "Ultra Bot detenido correctamente.")
    
    def save_settings():
        try:
            iterations = int(iter_entry.get())
            delay = int(time_entry.get())

            success = save_bot_settings(iterations, delay)
            if success:
                messagebox.showinfo("Configuración guardada", f"Iteraciones: {iterations}\nTiempo entre rondas: {delay} s")
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración en la base de datos.")

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa solo números enteros.")


    ctk.set_appearance_mode("dark")  # Modo oscuro
    ctk.set_default_color_theme("blue")  # Color primario

    # Crear ventana principal
    root = ctk.CTk()
    root.title("Ultra Bot")
    root.geometry("600x550")
    root.configure(fg_color="#FFFFFF")  # Fondo negro opaco (menos oscuro)

    # Etiqueta de bienvenida (más grande)
    welcome_label = ctk.CTkLabel(
        root,
        text=f"Bienvenido, {logged_in_user}",
        font=("Arial", 24, "bold"),
        text_color="black"  # Color del texto cambiado a negro
    )
    welcome_label.pack(anchor="w", padx=20, pady=20)

    def create_button(text, command, color):
        return ctk.CTkButton(
            root,
            text=text,
            command=command,
            font=("Arial", 12),
            fg_color=color,
            text_color="white",  # Texto negro
            corner_radius=10,
            width=250,
            height=40,
            border_color="black",
            border_width=2
        )

    # Contenedor para el contador y los botones
    # Un fondo gris oscuro para el contenedor
    left_frame = ctk.CTkFrame(root, width=300, fg_color="transparent")
    left_frame.pack(anchor="w", padx=20, pady=20)

    # Contador de cookies dentro del contenedor con fondo transparente
    file_label = ctk.CTkLabel(
        left_frame,
        text="Total de cookies en la base de datos: 0",
        wraplength=500,
        fg_color="transparent",  # Fondo del texto transparente
        text_color="black",  # Texto en negro
        font=("Arial", 16, "bold")  # Aumentar tamaño y hacerlo en negrita
    )
    file_label.pack(anchor="w", pady=10, padx=10)
    update_cookie_count()

    # Botón para cargar cookies
    process_button = create_button("Cargar Cookies", process_file, "#2644d9")
    process_button.pack(anchor="w", pady=5, padx=10)

    # Botón para limpiar base de datos
    clear_db_button = create_button("Limpiar Cookies", clear_db, "tomato")
    clear_db_button.pack(anchor="w", pady=5, padx=10)

    # Contenedor para los botones de ejecución del bot
    bot_frame = ctk.CTkFrame(root, fg_color="transparent")
    bot_frame.pack(anchor="w", padx=20, pady=20)

    # Etiqueta de título para los botones del bot
    bot_label = ctk.CTkLabel(
        bot_frame,
        text="Funcionalidades del Ultra Bot",
        font=("Arial", 16, "bold"),  # Hacerlo un poco más grande
        text_color="black"  # Texto en negro
    )
    bot_label.pack(anchor="w", pady=5, padx=10)

    # Botón para ejecutar el bot
    ultra_bot_button = create_button(
        "Ejecutar Ultra Bot", handle_ultra_bot, "#2644d9")
    ultra_bot_button.pack(anchor="w", pady=5, padx=10)

    # Botón para detener el bot
    stop_bot_button = create_button(
        "Detener Ultra Bot", handle_stop_ultra_bot, "tomato")
    stop_bot_button.pack(anchor="w", pady=5, padx=10)

    delete_folder_button = create_button(
        "Eliminar Archivos Cache de Ultra", handle_delete_ultra_folder, "red")
    delete_folder_button.pack(anchor="w", pady=5, padx=10)



    # Botón de Logout abajo a la derecha
    logout_button = ctk.CTkButton(
        root,
        text="Cerrar Sesión",
        command=handle_logout,
        font=("Arial", 14),
        fg_color="#FFFFFF",  # Gris oscuro
        text_color="black",
        corner_radius=10,
        width=160, height=40,  # Botón más pequeño en ancho
        border_color="black",  # Borde negro
        border_width=2,
        hover_color="tomato"  # Gris más oscuro al pasar el mouse
    )

    logout_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    # Etiqueta de firma en la esquina inferior izquierda
    signature_label = ctk.CTkLabel(
        root,
        text="Desarrollado por A. G.",
        font=("Arial", 10),  # Fuente más pequeña
        text_color="black"  # Texto negro
    )

    # Ubicarlo bien pegado al borde inferior
    signature_label.place(relx=0.0, rely=1.0, anchor="sw",
                        x=10, y=-5)  # Reduciendo margen inferior


    # Frame derecho para inputs personalizados
    right_frame = ctk.CTkFrame(root, width=250, fg_color="transparent")
    right_frame.place(relx=1.0, y=130, anchor="ne", x=-20)

    # Input: Número de iteraciones
    iter_label = ctk.CTkLabel(right_frame, text="Número de iteraciones:", text_color="black", font=("Arial", 12, "bold"))
    iter_label.pack(pady=(0, 2), anchor="w")
    iter_entry = ctk.CTkEntry(right_frame, width=200, placeholder_text="Ej: 10")
    iter_entry.pack(pady=(0, 5))

    # Input: Tiempo entre rondas (segundos)
    time_label = ctk.CTkLabel(right_frame, text="Tiempo entre rondas (s):", text_color="black", font=("Arial", 12, "bold"))
    time_label.pack(pady=(0, 2), anchor="w")
    time_entry = ctk.CTkEntry(right_frame, width=200, placeholder_text="Ej: 5")
    time_entry.pack(pady=(0, 10))

    # 🔽 Insertar valores guardados desde la base de datos (si existen)
    bot_settings = get_bot_settings()
    if bot_settings:
        iter_entry.insert(0, str(bot_settings["iterations"]))
        time_entry.insert(0, str(bot_settings["interval_seconds"]))


    # Botón para guardar
    save_button = ctk.CTkButton(right_frame, text="Guardar", command=save_settings, fg_color="#2644d9", text_color="white")
    save_button.pack(pady=10)  # Más cerca del input


    # Ejecutar el bucle principal
    root.mainloop()
