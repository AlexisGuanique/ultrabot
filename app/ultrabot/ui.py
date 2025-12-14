import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from app.database.database import save_cookies_to_db, clear_database, create_database, get_cookie_count, save_bot_settings, get_bot_settings, save_ultra_credentials, get_ultra_credentials, get_server_account_count, save_repetidas_settings, get_repetidas_settings
from app.ultrabot.file_handler import read_cookies_from_txt
from app.ultrabot.ultra_bot import execute_ultra_bot, stop_ultra_bot, execute_ultra_bot_repetidas, stop_ultra_bot_repetidas
from app.auth.auth import verify_token, logout
from app.ultrabot.auth_ui import setup_auth_ui
from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder


def setup_ui(logged_in_user, on_login_success):
    # Variables para los labels (necesarias para la función update_cookie_count)
    file_label = None
    server_label = None
    
    def update_cookie_count():
        """Actualiza el contador de cookies en la base de datos local y del servidor."""
        # Actualizar conteo local
        total_cookies = get_cookie_count()
        file_label.configure(
            text=f"Total de cuentas en la base de datos local: {total_cookies}")
        
        # Actualizar conteo del servidor
        server_count = get_server_account_count()
        if server_count is not None:
            server_label.configure(
                text=f"Total de cuentas en el servidor: {server_count}")
        else:
            server_label.configure(
                text="Total de cuentas en el servidor: Error al obtener")

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
    
    def handle_ultra_bot_repetidas():
        """Verifica el token antes de ejecutar el Ultra Bot de cuentas repetidas."""
        token_data = verify_token()
        if not (token_data and token_data.get("is_valid")):
            messagebox.showerror(
                "Usuario expirado", "Usuario expirado, por favor contacte con los desarrolladores.")
            logout()
            root.destroy()
            setup_auth_ui(on_login_success)
            return

        execute_ultra_bot_repetidas()  # Iniciar el bot de cuentas repetidas

    def handle_stop_ultra_bot_repetidas():
        """Detiene la ejecución del Ultra Bot de cuentas repetidas y muestra un mensaje de confirmación."""
        stop_ultra_bot_repetidas()
        print("🛑 Bot de cuentas repetidas detenido desde la UI.")
        messagebox.showinfo("Ultra Bot Repetidas", "Ultra Bot de cuentas repetidas detenido correctamente.")
    
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
    
    def save_repetidas_settings_ui():
        """Guarda la configuración de repetidas."""
        try:
            accounts_to_repeat = int(repetidas_accounts_entry.get())
            repetitions_count = int(repetidas_count_entry.get())
            interval_minutes = int(repetidas_time_entry.get())
            # Convertir minutos a segundos para guardar en la base de datos
            interval_seconds = interval_minutes * 60

            success = save_repetidas_settings(accounts_to_repeat, repetitions_count, interval_seconds)
            if success:
                messagebox.showinfo(
                    "Configuración guardada",
                    f"Cuentas a repetir: {accounts_to_repeat}\n"
                    f"Cantidad de repeticiones: {repetitions_count}\n"
                    f"Tiempo entre rondas: {interval_minutes} min"
                )
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración de repetidas en la base de datos.")

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa solo números enteros.")


    ctk.set_appearance_mode("dark")  # Modo oscuro
    ctk.set_default_color_theme("blue")  # Color primario

    # Crear ventana principal
    root = ctk.CTk()
    root.title("Ultra Bot")
    root.geometry("600x650")
    root.configure(fg_color="#FFFFFF")  # Fondo blanco

    # Crear frame scrollable para el contenido principal
    main_scrollable_frame = ctk.CTkScrollableFrame(
        root,
        fg_color="transparent",
        scrollbar_button_color="#888888",
        scrollbar_button_hover_color="#666666"
    )
    main_scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Etiqueta de bienvenida (más grande)
    welcome_label = ctk.CTkLabel(
        main_scrollable_frame,
        text=f"Bienvenido, {logged_in_user}",
        font=("Arial", 24, "bold"),
        text_color="black"  # Color del texto cambiado a negro
    )
    welcome_label.pack(anchor="w", padx=20, pady=20)

    def create_button(text, command, color):
        return ctk.CTkButton(
            main_scrollable_frame,
            text=text,
            command=command,
            font=("Arial", 12),
            fg_color=color,
            text_color="white",  # Texto blanco
            corner_radius=10,
            width=250,
            height=40,
            border_color="black",
            border_width=2
        )

    # Contenedor para el contador y los botones
    # Un fondo gris oscuro para el contenedor
    left_frame = ctk.CTkFrame(main_scrollable_frame, width=300, fg_color="transparent")
    left_frame.pack(anchor="w", padx=20, pady=20)

    # Contador de cuentas locales dentro del contenedor con fondo transparente
    file_label = ctk.CTkLabel(
        left_frame,
        text="Total de cuentas en la base de datos local: 0",
        wraplength=500,
        fg_color="transparent",  # Fondo del texto transparente
        text_color="black",  # Texto en negro
        font=("Arial", 16, "bold")  # Aumentar tamaño y hacerlo en negrita
    )
    file_label.pack(anchor="w", pady=10, padx=10)
    
    # Contador de cuentas del servidor
    server_label = ctk.CTkLabel(
        left_frame,
        text="Total de cuentas en el servidor: 0",
        wraplength=500,
        fg_color="transparent",  # Fondo del texto transparente
        text_color="black",  # Texto en negro
        font=("Arial", 16, "bold")  # Aumentar tamaño y hacerlo en negrita
    )
    server_label.pack(anchor="w", pady=10, padx=10)
    
    # Actualizar ambos contadores
    update_cookie_count()

    # Botón para limpiar base de datos
    clear_db_button = create_button("Limpiar Cookies", clear_db, "tomato")
    clear_db_button.pack(anchor="w", pady=5, padx=10)

    # Contenedor para los botones de ejecución del bot
    bot_frame = ctk.CTkFrame(main_scrollable_frame, fg_color="transparent")
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

    # Botón para ejecutar el bot de cuentas repetidas (justo debajo del botón anterior)
    ultra_bot_repetidas_button = create_button(
        "Ejecutar Bot Repetidas", handle_ultra_bot_repetidas, "#9b59b6")
    ultra_bot_repetidas_button.pack(anchor="w", pady=5, padx=10)

    # Botón para detener el bot
    stop_bot_button = create_button(
        "Detener Ultra Bot", handle_stop_ultra_bot, "tomato")
    stop_bot_button.pack(anchor="w", pady=5, padx=10)

    # Botón para detener el bot de cuentas repetidas
    stop_bot_repetidas_button = create_button(
        "Detener Bot Repetidas", handle_stop_ultra_bot_repetidas, "tomato")
    stop_bot_repetidas_button.pack(anchor="w", pady=5, padx=10)

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
    


   #! Frame derecho para inputs personalizados
    right_frame = ctk.CTkFrame(root, width=250, fg_color="transparent")
    right_frame.place(relx=1.0, y=150, anchor="ne", x=-20)

   # 🔽 Contenedor para inputs de Ultra (oculto al inicio)
    ultra_config_frame = ctk.CTkFrame(right_frame, fg_color="transparent")

    # 👉 Botón para mostrar/ocultar configuración de Ultra
    def toggle_ultra_inputs():
        if ultra_config_frame.winfo_ismapped():
            ultra_config_frame.pack_forget()
            toggle_ultra_button.configure(text="Configurar Ultra")
        else:
            ultra_config_frame.pack(pady=(10, 0), anchor="w")
            toggle_ultra_button.configure(text="Ocultar configuración")

    toggle_ultra_button = ctk.CTkButton(
        right_frame,
        text="Configurar Ultra",
        command=toggle_ultra_inputs,
        fg_color="#444",
        text_color="white"
    )
    toggle_ultra_button.pack(pady=(10, 5), anchor="w")

    # 👉 Input: Email de Ultra
    ultra_email_label = ctk.CTkLabel(
        ultra_config_frame,
        text="Email de Ultra:",
        text_color="black",
        font=("Arial", 12, "bold")
    )
    ultra_email_label.pack(pady=(0, 2), anchor="w")

    ultra_email_entry = ctk.CTkEntry(
        ultra_config_frame,
        width=200,
        placeholder_text="Ej: usuario@correo.com"
    )
    ultra_email_entry.pack(pady=(0, 5))

    # 👉 Input: Contraseña de Ultra
    ultra_pass_label = ctk.CTkLabel(
        ultra_config_frame,
        text="Contraseña de Ultra:",
        text_color="black",
        font=("Arial", 12, "bold")
    )
    ultra_pass_label.pack(pady=(0, 2), anchor="w")

    ultra_pass_frame = ctk.CTkFrame(ultra_config_frame, fg_color="transparent", width=200, height=40)
    ultra_pass_frame.pack(pady=(0, 10))

    ultra_pass_entry = ctk.CTkEntry(
        ultra_pass_frame,
        width=200,
        placeholder_text="••••••••",
        show="*"
    )
    ultra_pass_entry.pack(fill="both", expand=True)

    # 🔁 Alternar visibilidad
    def toggle_ultra_password():
        if ultra_pass_entry.cget("show") == "*":
            ultra_pass_entry.configure(show="")
            ultra_eye_button.configure(text="👁")  # Ojo abierto
        else:
            ultra_pass_entry.configure(show="*")
            ultra_eye_button.configure(text="🙈")  # Ojo cerrado

    ultra_eye_button = ctk.CTkButton(
        ultra_pass_frame,
        text="👁",
        width=20,
        height=20,
        command=toggle_ultra_password,
        fg_color="black",
        text_color="white",
        corner_radius=10,
        hover_color="black",
        border_width=0
    )
    ultra_eye_button.place(relx=0.88, rely=0.5, anchor="center")

    # 🔽 Cargar valores guardados (si existen)
    ultra_creds = get_ultra_credentials()
    if ultra_creds:
        ultra_email_entry.insert(0, ultra_creds["email"])
        ultra_pass_entry.insert(0, ultra_creds["password"])

    # 👉 Botón para guardar credenciales
    def save_ultra_credentials_ui():
        email = ultra_email_entry.get()
        password = ultra_pass_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Por favor completa ambos campos.")
            return

        save_ultra_credentials(email, password)
        messagebox.showinfo("Guardado", "✅ Credenciales de Ultra guardadas correctamente.")

    save_ultra_button = ctk.CTkButton(
        ultra_config_frame,
        text="Guardar Credenciales",
        command=save_ultra_credentials_ui,
        fg_color="#0066cc",
        text_color="white"
    )
    save_ultra_button.pack(pady=(0, 15))

    #! 🔽 Contenedor oculto para la configuración del bot
    bot_config_frame = ctk.CTkFrame(right_frame, fg_color="transparent")

    # 👉 Botón para mostrar/ocultar inputs del bot
    def toggle_bot_inputs():
        if bot_config_frame.winfo_ismapped():
            bot_config_frame.pack_forget()
            toggle_bot_button.configure(text="Configurar Bot")
        else:
            bot_config_frame.pack(pady=(10, 0), anchor="w")
            toggle_bot_button.configure(text="Ocultar configuración")

    toggle_bot_button = ctk.CTkButton(
        right_frame,
        text="Configurar Bot",
        command=toggle_bot_inputs,
        fg_color="#444",
        text_color="white"
    )
    toggle_bot_button.pack(pady=(10, 5), anchor="w")

    # 👉 Input: Número de iteraciones
    iter_label = ctk.CTkLabel(bot_config_frame, text="Número de iteraciones:", text_color="black", font=("Arial", 12, "bold"))
    iter_label.pack(pady=(0, 2), anchor="w")
    iter_entry = ctk.CTkEntry(bot_config_frame, width=200, placeholder_text="Ej: 10")
    iter_entry.pack(pady=(0, 5))

    # 👉 Input: Tiempo entre rondas (segundos)
    time_label = ctk.CTkLabel(bot_config_frame, text="Tiempo entre rondas (s):", text_color="black", font=("Arial", 12, "bold"))
    time_label.pack(pady=(0, 2), anchor="w")
    time_entry = ctk.CTkEntry(bot_config_frame, width=200, placeholder_text="Ej: 5")
    time_entry.pack(pady=(0, 10))

    # 🔽 Insertar valores guardados desde la base de datos (si existen)
    bot_settings = get_bot_settings()
    if bot_settings:
        iter_entry.insert(0, str(bot_settings["iterations"]))
        time_entry.insert(0, str(bot_settings["interval_seconds"]))

    # 👉 Botón para guardar configuración del bot
    save_button = ctk.CTkButton(
        bot_config_frame,
        text="Guardar",
        command=save_settings,
        fg_color="#2644d9",
        text_color="white"
    )
    save_button.pack(pady=10)

    #! 🔽 Contenedor oculto para la configuración de repetidas
    repetidas_config_frame = ctk.CTkFrame(right_frame, fg_color="transparent")

    # 👉 Botón para mostrar/ocultar inputs de repetidas
    def toggle_repetidas_inputs():
        if repetidas_config_frame.winfo_ismapped():
            repetidas_config_frame.pack_forget()
            toggle_repetidas_button.configure(text="Configurar Repetidas")
        else:
            repetidas_config_frame.pack(pady=(10, 0), anchor="w")
            toggle_repetidas_button.configure(text="Ocultar configuración")

    toggle_repetidas_button = ctk.CTkButton(
        right_frame,
        text="Configurar Repetidas",
        command=toggle_repetidas_inputs,
        fg_color="#444",
        text_color="white"
    )
    toggle_repetidas_button.pack(pady=(10, 5), anchor="w")

    # 👉 Input: Cuentas a repetir
    repetidas_accounts_label = ctk.CTkLabel(
        repetidas_config_frame,
        text="Cuentas a repetir:",
        text_color="black",
        font=("Arial", 12, "bold")
    )
    repetidas_accounts_label.pack(pady=(0, 2), anchor="w")
    repetidas_accounts_entry = ctk.CTkEntry(
        repetidas_config_frame,
        width=200,
        placeholder_text="Ej: 5"
    )
    repetidas_accounts_entry.pack(pady=(0, 5))

    # 👉 Input: Cantidad de repeticiones
    repetidas_count_label = ctk.CTkLabel(
        repetidas_config_frame,
        text="Cantidad de repeticiones:",
        text_color="black",
        font=("Arial", 12, "bold")
    )
    repetidas_count_label.pack(pady=(0, 2), anchor="w")
    repetidas_count_entry = ctk.CTkEntry(
        repetidas_config_frame,
        width=200,
        placeholder_text="Ej: 3"
    )
    repetidas_count_entry.pack(pady=(0, 5))

    # 👉 Input: Tiempo entre rondas de repetidas (minutos)
    repetidas_time_label = ctk.CTkLabel(
        repetidas_config_frame,
        text="Tiempo entre rondas de repetidas (min):",
        text_color="black",
        font=("Arial", 12, "bold")
    )
    repetidas_time_label.pack(pady=(0, 2), anchor="w")
    repetidas_time_entry = ctk.CTkEntry(
        repetidas_config_frame,
        width=200,
        placeholder_text="Ej: 120"
    )
    repetidas_time_entry.pack(pady=(0, 10))

    # 🔽 Insertar valores guardados desde la base de datos (si existen)
    repetidas_settings = get_repetidas_settings()
    if repetidas_settings:
        repetidas_accounts_entry.insert(0, str(repetidas_settings["accounts_to_repeat"]))
        repetidas_count_entry.insert(0, str(repetidas_settings["repetitions_count"]))
        # Convertir segundos a minutos para mostrar en la UI
        interval_seconds = repetidas_settings["interval_seconds"]
        interval_minutes = interval_seconds // 60
        repetidas_time_entry.insert(0, str(interval_minutes))

    # 👉 Botón para guardar configuración de repetidas
    save_repetidas_button = ctk.CTkButton(
        repetidas_config_frame,
        text="Guardar",
        command=save_repetidas_settings_ui,
        fg_color="#9b59b6",
        text_color="white"
    )
    save_repetidas_button.pack(pady=10)





    # Ejecutar el bucle principal
    root.mainloop()
