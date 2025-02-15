import os
import shutil
import tkinter as tk
from tkinter import messagebox

# Ruta de la carpeta a eliminar
TARGET_FOLDER = r"C:\Users\Administrator\AppData\Roaming\Ultra"


def handle_delete_ultra_folder():
    """Elimina la carpeta Ultra si existe"""
    if os.path.exists(TARGET_FOLDER):
        confirm = messagebox.askyesno(
            "Confirmación", f"¿Seguro que deseas eliminar '{TARGET_FOLDER}'?")
        if confirm:
            try:
                shutil.rmtree(TARGET_FOLDER)
                messagebox.showinfo(
                    "Éxito", "Carpeta eliminada correctamente.")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar la carpeta: {e}")
        else:
            messagebox.showinfo("Cancelado", "Operación cancelada.")
    else:
        messagebox.showwarning("Advertencia", "La carpeta no existe.")
