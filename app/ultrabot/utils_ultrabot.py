import os
import shutil
from tkinter import messagebox

USER_HOME = os.path.expanduser("~")
TARGET_FOLDER = os.path.join(USER_HOME, "AppData", "Roaming", "Ultra")

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
