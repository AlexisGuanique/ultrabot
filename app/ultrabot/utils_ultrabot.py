import os
import shutil
import psutil
import time
from tkinter import messagebox

USER_HOME = os.path.expanduser("~")
TARGET_FOLDER = os.path.join(USER_HOME, "AppData", "Roaming", "Ultra")

# Nombres de procesos relacionados con Ultra que deben detenerse
ULTRA_PROCESS_NAMES = [
    "Ultra.exe",
    "ultra.exe", 
    "Ultra",
    "ultra",
    "UltraBrowser.exe",
    "ultrabrowser.exe",
    "UltraBrowser",
    "ultrabrowser"
]

def kill_ultra_processes(show_confirmation=True):
    """Detiene todos los procesos relacionados con Ultra que estén ejecutándose
    
    Args:
        show_confirmation (bool): Si True, muestra información sobre los procesos detenidos.
                                 Si False, detiene silenciosamente.
    
    Returns:
        bool: True si se detuvieron procesos o no había procesos ejecutándose, False en caso de error.
    """
    import subprocess
    
    try:
        killed_processes = []
        
        # Usar PowerShell para encontrar procesos de Ultra (más confiable en Windows)
        print("🔍 Buscando procesos de Ultra...")
        
        # Buscar procesos con diferentes variantes del nombre
        ultra_variants = ["Ultra", "ultra", "Ultra.exe", "ultra.exe"]
        
        for variant in ultra_variants:
            try:
                # Comando PowerShell para encontrar procesos
                cmd = f'powershell "Get-Process {variant} -ErrorAction SilentlyContinue | Select-Object ProcessName, Id, Path"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f"📋 Procesos encontrados para '{variant}':")
                    print(result.stdout)
                    
                    # Parsear la salida para obtener los PIDs
                    lines = result.stdout.strip().split('\n')
                    for line in lines[2:]:  # Saltar encabezados
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    pid = int(parts[1])
                                    proc_name = parts[0]
                                    
                                    print(f"🛑 Deteniendo proceso: {proc_name} (PID: {pid})")
                                    
                                    # Terminar el proceso usando PowerShell
                                    kill_cmd = f'powershell "Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"'
                                    kill_result = subprocess.run(kill_cmd, shell=True, capture_output=True, text=True, timeout=5)
                                    
                                    if kill_result.returncode == 0:
                                        killed_processes.append(f"{proc_name} (PID: {pid})")
                                        print(f"✅ Proceso {proc_name} (PID: {pid}) detenido correctamente")
                                    else:
                                        print(f"❌ No se pudo detener {proc_name} (PID: {pid}): {kill_result.stderr}")
                                        
                                except (ValueError, IndexError):
                                    continue
                                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout al buscar procesos de '{variant}'")
                continue
            except Exception as e:
                print(f"⚠️ Error al buscar procesos de '{variant}': {e}")
                continue
        
        # Esperar un momento para que los procesos se terminen
        if killed_processes:
            print("⏳ Esperando a que los procesos se terminen...")
            time.sleep(3)
            
            # Verificar que los procesos se hayan detenido
            print("🔍 Verificando que los procesos se hayan detenido...")
            remaining_found = False
            
            for variant in ultra_variants:
                try:
                    verify_cmd = f'powershell "Get-Process {variant} -ErrorAction SilentlyContinue"'
                    verify_result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True, timeout=5)
                    
                    if verify_result.returncode == 0 and verify_result.stdout.strip():
                        print(f"⚠️ Aún hay procesos de '{variant}' ejecutándose:")
                        print(verify_result.stdout)
                        remaining_found = True
                        
                except Exception as e:
                    print(f"⚠️ Error al verificar procesos de '{variant}': {e}")
                    continue
            
            if remaining_found:
                print("❌ Algunos procesos de Ultra aún están ejecutándose")
                return False
            else:
                print(f"✅ Se detuvieron {len(killed_processes)} procesos de Ultra correctamente")
                if show_confirmation and killed_processes:
                    messagebox.showinfo("Procesos detenidos", 
                                      f"Se detuvieron {len(killed_processes)} procesos de Ultra:\n" + 
                                      "\n".join(killed_processes))
                return True
        else:
            print("ℹ️ No se encontraron procesos de Ultra ejecutándose")
            return True
            
    except Exception as e:
        print(f"❌ Error al detener procesos de Ultra: {e}")
        if show_confirmation:
            messagebox.showerror("Error", f"No se pudieron detener los procesos de Ultra: {e}")
        return False

def wait_for_processes_to_stop(process_names, max_wait_time=10):
    """Espera hasta que los procesos especificados se detengan completamente
    
    Args:
        process_names (list): Lista de nombres de procesos a verificar
        max_wait_time (int): Tiempo máximo en segundos para esperar
    
    Returns:
        bool: True si todos los procesos se detuvieron, False si algunos siguen ejecutándose
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        remaining_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ""
                
                for process_name in process_names:
                    if process_name.lower() in proc_name or process_name.lower() in proc_exe:
                        remaining_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                        break
            except:
                continue
        
        if not remaining_processes:
            print("✅ Todos los procesos de Ultra se detuvieron correctamente")
            return True
        
        time.sleep(1)  # Verificar cada segundo
    
    print(f"⚠️ Algunos procesos de Ultra aún están ejecutándose después de {max_wait_time} segundos: {remaining_processes}")
    return False

def handle_delete_ultra_folder(show_confirmation=True, max_wait_time=30):
    """Elimina la carpeta Ultra si existe y verifica que se eliminó correctamente
    
    Args:
        show_confirmation (bool): Si True, muestra diálogos de confirmación y resultado.
                                 Si False, elimina silenciosamente sin confirmación.
        max_wait_time (int): Tiempo máximo en segundos para esperar a que la eliminación termine.
    
    Returns:
        bool: True si la carpeta se eliminó correctamente, False en caso contrario.
    """
    import time
    
    if os.path.exists(TARGET_FOLDER):
        if show_confirmation:
            confirm = messagebox.askyesno(
                "Confirmación", f"¿Seguro que deseas eliminar '{TARGET_FOLDER}'?")
            if confirm:
                try:
                    shutil.rmtree(TARGET_FOLDER)
                    # Verificar que se eliminó correctamente
                    if wait_for_folder_deletion(TARGET_FOLDER, max_wait_time):
                        messagebox.showinfo(
                            "Éxito", "Carpeta eliminada correctamente.")
                        return True
                    else:
                        messagebox.showerror(
                            "Error", "La carpeta no se eliminó completamente en el tiempo esperado.")
                        return False
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"No se pudo eliminar la carpeta: {e}")
                    return False
            else:
                messagebox.showinfo("Cancelado", "Operación cancelada.")
                return False
        else:
            # Eliminación silenciosa para uso en el ciclo de la aplicación
            try:
                print("🗑️ Iniciando eliminación de cache de Ultra...")
                shutil.rmtree(TARGET_FOLDER)
                print("⏳ Verificando que la eliminación se complete...")
                
                # Verificar que se eliminó correctamente
                if wait_for_folder_deletion(TARGET_FOLDER, max_wait_time):
                    print("✅ Cache de Ultra eliminado correctamente")
                    return True
                else:
                    print("❌ La eliminación de cache no se completó en el tiempo esperado")
                    return False
            except Exception as e:
                print(f"❌ Error al eliminar cache de Ultra: {e}")
                return False
    else:
        if show_confirmation:
            messagebox.showwarning("Advertencia", "La carpeta no existe.")
        else:
            print("⚠️ La carpeta de cache no existe")
        return True  # No existe, consideramos que está "eliminada"

def wait_for_folder_deletion(folder_path, max_wait_time=30):
    """Espera hasta que una carpeta se elimine completamente
    
    Args:
        folder_path (str): Ruta de la carpeta a verificar
        max_wait_time (int): Tiempo máximo en segundos para esperar
    
    Returns:
        bool: True si la carpeta se eliminó, False si no se eliminó en el tiempo esperado
    """
    import time
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if not os.path.exists(folder_path):
            print(f"✅ Verificación exitosa: La carpeta '{folder_path}' se eliminó correctamente")
            return True
        time.sleep(1)  # Verificar cada segundo
    
    print(f"❌ Timeout: La carpeta '{folder_path}' aún existe después de {max_wait_time} segundos")
    return False
