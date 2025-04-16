import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.auth.auth import logout
import threading
from tkinter import messagebox
from ..profile_opener import openProfileWithExtraExtension
from ...run_checker import run_checker
from ..utils.file_reader import read_cookies_from_txt
from ..utils.click_coordenadas import get_mouse_coordinate_on_keypress
from ....database.database import save_account_cookie, save_coordinates, get_coordinates, count_account_cookies, clear_cookies


def setup_checker_ui(logged_in_user, on_login_success):

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Ultra Checker")
    root.geometry("600x550")
    root.configure(fg_color="#FFFFFF")

    # Etiqueta de bienvenida
    welcome_label = ctk.CTkLabel(
        root,
        text=f"Ultra Checker - Bienvenido, {logged_in_user}",
        font=("Arial", 24, "bold"),
        text_color="black"
    )
    welcome_label.pack(anchor="w", padx=20, pady=20)

    cookie_count_label = ctk.CTkLabel(
        root,
        text=f"Cookies almacenadas: {count_account_cookies()}",
        font=("Arial", 14, "bold"),
        text_color="black"
    )
    cookie_count_label.pack(anchor="w", padx=20, pady=(10, 0))
    # Función para crear botones con estilo consistente

    def create_button(text, command, color):
        return ctk.CTkButton(
            root,
            text=text,
            command=command,
            font=("Arial", 12),
            fg_color=color,
            text_color="white",
            corner_radius=10,
            width=250,
            height=40,
            border_color="black",
            border_width=2
        )

    def process_accounts_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Seleccionar archivo de cookies"
        )
        if file_path:
            try:
                cookies = read_cookies_from_txt(file_path)
                if cookies:
                    for item in cookies:
                        save_account_cookie(item["cookie"])
                    cookie_count_label.configure(text=f"Cookies almacenadas: {count_account_cookies()}")

                    messagebox.showinfo(
                        "Ultra Checker",
                        f"✅ Se importaron {len(cookies)} cookies correctamente."
                    )
                else:
                    messagebox.showwarning(
                        "Ultra Checker",
                        "⚠️ El archivo no contiene cookies válidas."
                    )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"❌ Ocurrió un error al procesar el archivo:\n{e}"
                )

        # 🔹 Mostrar coordenadas guardadas

    # Botón para cargar cuentas
    load_button = create_button(
        "Cargar Cuentas", process_accounts_file, "#2644d9")
    load_button.pack(anchor="w", padx=20, pady=10)

    def add_coordinates_interactively():
        etiquetas = ["cookieEditor", "cookieEditorOption", "cookieEditionImport", "cookieEditorExport"]
        coordenadas = []

        # 🔹 Abrir Chrome antes de iniciar la captura
        driver = openProfileWithExtraExtension()
        driver.get("https://www.linkedin.com/")

        def capturar_y_mostrar(index, popup):
            popup.lift()
            popup.focus_force()
            popup.attributes("-topmost", True)

            label = ctk.CTkLabel(
                popup,
                text=f"Presiona la tecla 'c' para capturar la coordenada de:\n{etiquetas[index]}",
                font=("Arial", 14),
                text_color="black"
            )
            label.pack(pady=15)

            coord_label = ctk.CTkLabel(
                popup,
                text="",
                font=("Arial", 14, "bold"),
                text_color="black"
            )
            coord_label.pack(pady=10)

            def capturar():
                coord = get_mouse_coordinate_on_keypress("c")
                coordenadas.append(coord)
                popup.after(0, lambda: coord_label.configure(
                    text=f"{etiquetas[index]}: {coord}"))

            threading.Thread(target=capturar, daemon=True).start()

            def siguiente():
                popup.destroy()
                if index + 1 < len(etiquetas):
                    mostrar_popup(index + 1)
                else:
                    save_coordinates(*coordenadas)
                    popup.after(0, lambda: messagebox.showinfo(
                        "Guardado", "✅ Coordenadas guardadas correctamente.")
                    )

                    try:
                        driver.quit()  # 🔹 Cierra la ventana de Chrome
                    except Exception as e:
                        print(f"❌ Error al cerrar Chrome: {e}")

            next_button = ctk.CTkButton(
                popup,
                text="Próxima coordenada",
                command=siguiente,
                fg_color="#5C2D91",
                text_color="white",
                hover_color="#472173"
            )
            next_button.pack(pady=15)

        def mostrar_popup(index):
            popup = ctk.CTkToplevel()
            popup.geometry("420x220")
            popup.title("Captura de Coordenada")
            popup.configure(fg_color="#f0f0f0")
            capturar_y_mostrar(index, popup)

        mostrar_popup(0)

    def show_coordinates():
        coordinates = get_coordinates()
        coordinates_box.configure(state="normal")
        coordinates_box.delete("0.0", "end")

        if coordinates:
            labels = ["cookieEditor", "cookieEditorOption",
                      "cookieEditionImport", "cookieEditorExport"]
            for label, coord in zip(labels, coordinates):
                coordinates_box.insert("end", f"{label}: {coord}\n")
        else:
            coordinates_box.insert(
                "0.0", "❌ No se encontraron coordenadas guardadas.")

        coordinates_box.configure(state="disabled")

    def start_checker():
        # Ejecutar la función run_checker en un hilo separado para no bloquear la UI
        threading.Thread(target=run_checker, daemon=True).start()

    # Botón para iniciar el chequeo de cuentas
    check_button = create_button("Iniciar Chequeo", start_checker, "green")
    check_button.pack(anchor="w", padx=20, pady=10)

 # Botón para guardar coordenadas
    coordinates_button = create_button(
        "Guardar Coordenadas", add_coordinates_interactively, "#a147d1"
    )
    coordinates_button.place(relx=1.0, x=-5, y=115, anchor="ne")
    # Función para manejar el logout

    def handle_logout():
        if logout():
            messagebox.showinfo("Logout Exitoso", "Has cerrado sesión.")
            root.destroy()
            from app.ultrabot.auth_ui import setup_auth_ui
            setup_auth_ui(on_login_success)
        else:
            messagebox.showwarning("Error", "No hay ningún usuario logueado.")

    logout_button = ctk.CTkButton(
        root,
        text="Cerrar Sesión",
        command=handle_logout,
        font=("Arial", 14),
        fg_color="#FFFFFF",
        text_color="black",
        corner_radius=10,
        width=160,
        height=40,
        border_color="black",
        border_width=2,
        hover_color="tomato"
    )
    logout_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    # Etiqueta de firma en la esquina inferior izquierda
    signature_label = ctk.CTkLabel(
        root,
        text="Desarrollado por A. G.",
        font=("Arial", 10),
        text_color="black"
    )
    signature_label.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-5)

    # Botón para mostrar coordenadas
    coord_button = create_button(
        "Mostrar Coordenadas", show_coordinates, "#8a2be2"
    )
    coord_button.place(relx=1.0, x=-5, y=165, anchor="ne")

    # Cuadro de coordenadas
    coordinates_box = ctk.CTkTextbox(
        root,
        width=250,
        height=120,
        font=("Arial", 12),
        corner_radius=10,
        fg_color="black",
        text_color="white",
        border_color="#8a2be2",
        border_width=2
    )
    coordinates_box.insert(
        "0.0", "Presiona el botón para mostrar coordenadas..."
    )
    coordinates_box.configure(state="disabled")
    coordinates_box.place(relx=1.0, x=-5, y=225, anchor="ne")

    def handle_clear_cookies():
        confirm = messagebox.askyesno(
            "Confirmar acción",
            "¿Estás seguro de que deseas eliminar todas las cookies guardadas?"
        )
        if confirm:
            clear_cookies()
            messagebox.showinfo("Limpieza completada",
                                "✅ Se han eliminado todas las cookies.")
            cookie_count_label.configure(
                text=f"Cookies almacenadas: {count_account_cookies()}")

    clear_button = create_button(
        "Limpiar Cookies", handle_clear_cookies, "#D91E1E")
    clear_button.pack(anchor="w", padx=20, pady=10)

    root.mainloop()


if __name__ == "__main__":
    setup_checker_ui("Usuario de Prueba", lambda data: print(
        "Callback on login success"))
