import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from app.database.database import save_cookies_to_db, clear_database, create_database, get_cookie_count, get_email_by_id
from app.ultrabot.file_handler import read_cookies_from_txt
from app.ultrabot.ultra_bot import execute_ultra_bot, stop_ultra_bot, get_failed_logins_summary
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
        confirm = messagebox.askyesno(
            "Confirmar acción", "¿Seguro que quieres limpiar las Cookies?")
        if confirm:
            try:
                clear_database()
                update_cookie_count()
                messagebox.showinfo(
                    "Cookies Limpiadas", "Todas las cookies fueron eliminadas exitosamente.")
            except Exception as e:
                messagebox.showerror(
                    "Error al Limpiar", f"Se produjo un error al limpiar la base de datos:\n{e}")
        else:
            messagebox.showinfo("Acción cancelada",
                                "No se han eliminado las Cookies.")

    def handle_logout():
        from app.ultrabot.auth_ui import setup_auth_ui
        if logout():
            messagebox.showinfo("Logout Exitoso", "Has cerrado sesión.")
            root.destroy()
            setup_auth_ui(on_login_success)
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
        execute_ultra_bot()

    

    def handle_stop_ultra_bot():
        stop_ultra_bot()
        print("🛑 Bot detenido desde la UI.")
        messagebox.showinfo("Ultra Bot", "Ultra Bot detenido correctamente.")
        update_failed_logins_summary()

    def update_failed_logins_summary():

        summary = get_failed_logins_summary()
        failed_ids = summary["failed_ids"]

        # Obtener el total de cookies en la base de datos
        total_cookies = get_cookie_count()
        failed_count = len(failed_ids)


        def update_ui():
            failed_logins_textbox.configure(state="normal")  # Habilita edición temporalmente
            failed_logins_textbox.delete("1.0", tk.END)  # Borra contenido previo

            # 🔹 Agregar resumen
            summary_text = f"📌 Total de cookies en la base de datos: {total_cookies}\n"
            summary_text += f"❌ No lograron loguear: {failed_count}\n\n"

            # 🔹 Agregar detalles de las cookies fallidas
            if failed_ids:
                summary_text += "📛 Emails de cookies fallidas:\n"
                for cookie_id in failed_ids:
                    email = get_email_by_id(cookie_id)  # Obtener el email
                    if email:
                        summary_text += f"  - {email}\n"
                    else:
                        summary_text += f"  - ID {cookie_id} (sin email registrado)\n"
            else:
                summary_text += "✅ No hubo fallos en el login."

            failed_logins_textbox.insert(tk.END, summary_text)  # Inserta los datos
            failed_logins_textbox.configure(state="disabled")  # Deshabilita edición

        root.after(100, update_ui)  # 🔹 Ejecuta en el hilo principal para evitar bloqueos


    def set_update_callback(callback):
        """Guarda la función de actualización para que ultra_bot.py pueda llamarla."""
        global update_failed_logins_summary_callback
        update_failed_logins_summary_callback = callback

    from app.ultrabot.ultra_bot import set_update_callback

    # Pasar la función update_failed_logins_summary a ultra_bot.py
    set_update_callback(update_failed_logins_summary)


    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Ultra Bot")
    root.geometry("800x550")
    root.configure(fg_color="#FFFFFF")

    welcome_label = ctk.CTkLabel(
        root, text=f"Bienvenido, {logged_in_user}", font=("Arial", 24, "bold"), text_color="black"
    )
    welcome_label.pack(anchor="w", padx=20, pady=20)

    # Contenedor principal sin expandirse innecesariamente
    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=False, padx=20, pady=20)

    left_frame = ctk.CTkFrame(main_frame, width=300, fg_color="transparent")
    left_frame.pack(side="left", anchor="w", padx=10, pady=10, fill="y")

    file_label = ctk.CTkLabel(
        left_frame, text="Total de cookies en la base de datos: 0",
        wraplength=500, fg_color="transparent", text_color="black", font=("Arial", 16, "bold")
    )
    file_label.pack(anchor="w", pady=10, padx=10)
    update_cookie_count()

    def create_button(text, command, color):
        return ctk.CTkButton(
            left_frame, text=text, command=command, font=("Arial", 12),
            fg_color=color, text_color="white", corner_radius=10,
            width=250, height=40, border_color="black", border_width=2
        )

    process_button = create_button("Cargar Cookies", process_file, "#2644d9")
    process_button.pack(anchor="w", pady=5, padx=10)

    clear_db_button = create_button("Limpiar Cookies", clear_db, "tomato")
    clear_db_button.pack(anchor="w", pady=5, padx=10)

    bot_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
    bot_frame.pack(anchor="w", padx=10, pady=10)

    bot_label = ctk.CTkLabel(
        bot_frame, text="Funcionalidades del Ultra Bot", font=("Arial", 16, "bold"), text_color="black"
    )
    bot_label.pack(anchor="w", pady=5, padx=10)

    ultra_bot_button = create_button(
        "Ejecutar Ultra Bot", handle_ultra_bot, "#2644d9")
    ultra_bot_button.pack(anchor="w", pady=5, padx=10)

    stop_bot_button = create_button(
        "Detener Ultra Bot", handle_stop_ultra_bot, "tomato")
    stop_bot_button.pack(anchor="w", pady=5, padx=10)

    delete_folder_button = create_button(
        "Eliminar Archivos Cache de Ultra", handle_delete_ultra_folder, "red")
    delete_folder_button.pack(anchor="w", pady=5, padx=10)



    # Contenedor derecho (resumen de ejecución) con mayor altura
    right_frame = ctk.CTkFrame(main_frame, width=450, height=370, fg_color="lightgray")  # 🔹 Aumentado el alto
    right_frame.pack(side="right", anchor="n", padx=10, pady=25)

    summary_label = ctk.CTkLabel(
        right_frame, text="Resumen de ultima carga", font=("Arial", 18, "bold"), text_color="black"
    )
    summary_label.pack(anchor="center", pady=5)

    # Cuadro de texto con mayor altura
    failed_logins_textbox = ctk.CTkTextbox(
        right_frame, width=430, height=300, wrap="word", font=("Arial", 16), text_color="black", fg_color="white"  # 🔹 Más alto
    )
    failed_logins_textbox.pack(padx=10, pady=5)
    failed_logins_textbox.configure(state="disabled")

    # 🔹 Botón de Logout sigue FUERA de `right_frame`
    logout_button = ctk.CTkButton(
        root,  # 🔹 Sigue estando en `root`, no en `right_frame`
        text="Cerrar Sesión",
        command=handle_logout,
        font=("Arial", 16),
        fg_color="#FFFFFF",  
        text_color="black",
        corner_radius=10,
        width=120, height=35,
        border_color="black",
        border_width=2,
        hover_color="tomato"
    )

    # 🔹 Ubicamos el botón en la parte inferior derecha de la ventana
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
                        x=10, y=-5)


    root.mainloop()
