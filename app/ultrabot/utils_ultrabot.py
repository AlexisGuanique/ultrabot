import os
import shutil
from tkinter import messagebox

USER_HOME = os.path.expanduser("~")
TARGET_FOLDER = os.path.join(USER_HOME, "AppData", "Roaming", "Ultra")

def handle_delete_ultra_folder(show_confirmation=True):
    """Elimina la carpeta Ultra si existe
    
    Args:
        show_confirmation (bool): Si True, muestra diálogos de confirmación y resultado.
                                 Si False, elimina silenciosamente sin confirmación.
    """
    if os.path.exists(TARGET_FOLDER):
        if show_confirmation:
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
            # Eliminación silenciosa para uso en el ciclo de la aplicación
            try:
                shutil.rmtree(TARGET_FOLDER)
                print("✅ Cache de Ultra eliminado correctamente")
            except Exception as e:
                print(f"❌ Error al eliminar cache de Ultra: {e}")
    else:
        if show_confirmation:
            messagebox.showwarning("Advertencia", "La carpeta no existe.")
        else:
            print("⚠️ La carpeta de cache no existe")
