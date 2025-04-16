import customtkinter as ctk
import tkinter as tk


def choice_dialog(title, message):
    """
    Muestra un diálogo con el título y mensaje indicados y dos botones:
    "UltraBot" y "Checker".
    Retorna "UltraBot" o "Checker" según la elección del usuario.
    """
    # Crear ventana de diálogo usando CTkToplevel de customtkinter
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.configure(fg_color="#FFFFFF") 
    
    dialog.grab_set()

    
    label = ctk.CTkLabel(dialog, text=message, font=(
        "Arial", 14, "bold"), text_color="black", fg_color="transparent")
    label.pack(pady=20)

    choice_var = tk.StringVar(value="")

    def select(option):
        choice_var.set(option)
        dialog.destroy()

    button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    button_frame.pack(pady=10)

    btn_ultrabot = ctk.CTkButton(
        button_frame,
        text="UltraBot",
        command=lambda: select("UltraBot"),
        width=150,
        height=50,                    # Altura mayor
        fg_color="#2644d9",
        text_color="white",
        corner_radius=10,
        border_color="black",         # Borde negro
        border_width=2                # Grosor del borde
    )
    btn_ultrabot.pack(side="left", padx=10)

    # Botón Checker
    btn_checker = ctk.CTkButton(
        button_frame,
        text="Checker",
        command=lambda: select("Checker"),
        width=150,
        height=50,                    # Altura mayor
        fg_color="tomato",
        text_color="black",
        corner_radius=10,
        border_color="black",         # Borde negro
        border_width=2                # Grosor del borde
    )
    btn_checker.pack(side="left", padx=10)

    # Esperar a que el diálogo se cierre para obtener la elección
    dialog.wait_window()
    return choice_var.get()
