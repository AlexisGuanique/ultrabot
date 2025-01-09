import tkinter as tk
from tkinter import filedialog, messagebox
import json
from database import save_cookies_to_db
from file_handler import read_cookies_from_txt

def setup_ui():
    """Configura la ventana principal de la aplicación."""
    def select_file():
        """Abre un cuadro de diálogo para seleccionar un archivo .txt."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Seleccionar archivo de texto"
        )
        if file_path:
            file_label.config(text=f"Archivo seleccionado: {file_path}")
            return file_path
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
            return None

    def process_file():
        """Lee las cookies desde el archivo seleccionado y las guarda en la base de datos."""
        file_path = select_file()
        if file_path:
            cookies = read_cookies_from_txt(file_path)
            if cookies:
                save_cookies_to_db(cookies)
                messagebox.showinfo("Éxito", f"Se guardaron {len(cookies)} cookies en la base de datos.")
            else:
                messagebox.showerror("Error", "No se pudieron leer cookies del archivo.")

    # Crear ventana principal
    root = tk.Tk()
    root.title("Gestor de Cookies")
    root.geometry("600x400")

    # Etiqueta de bienvenida
    welcome_label = tk.Label(root, text="Bienvenido al Gestor de Cookies", font=("Arial", 16))
    welcome_label.pack(pady=20)

    # Etiqueta para mostrar el archivo seleccionado
    file_label = tk.Label(root, text="No se ha seleccionado ningún archivo", wraplength=500)
    file_label.pack(pady=10)

    # Botón para procesar archivo
    process_button = tk.Button(root, text="Cargar Cookies", command=process_file, font=("Arial", 12))
    process_button.pack(pady=10)

    # Ejecutar el bucle principal
    root.mainloop()
