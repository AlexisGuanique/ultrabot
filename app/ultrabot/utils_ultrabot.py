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
    import os
    import sys
    
    try:
        killed_processes = []
        
        # PROTECCIÓN CRÍTICA: Obtener información completa del proceso del bot usando psutil
        protected_pids = set()
        protected_paths = set()
        
        try:
            current_process = psutil.Process()
            current_pid = current_process.pid
            protected_pids.add(current_pid)
            
            # Obtener la ruta del ejecutable del proceso actual
            try:
                current_exe = current_process.exe().lower() if current_process.exe() else ""
                if current_exe:
                    protected_paths.add(current_exe)
                    # También agregar el directorio del ejecutable
                    protected_paths.add(os.path.dirname(current_exe).lower())
            except:
                pass
            
            # Obtener la ruta del script Python si está disponible
            try:
                if hasattr(sys, 'executable'):
                    python_exe = sys.executable.lower()
                    protected_paths.add(python_exe)
                    protected_paths.add(os.path.dirname(python_exe).lower())
            except:
                pass
            
            # Obtener el proceso padre si existe
            try:
                parent = current_process.parent()
                if parent:
                    protected_pids.add(parent.pid)
                    try:
                        parent_exe = parent.exe().lower() if parent.exe() else ""
                        if parent_exe:
                            protected_paths.add(parent_exe)
                            protected_paths.add(os.path.dirname(parent_exe).lower())
                    except:
                        pass
            except:
                pass
            
            # Obtener procesos hijos del bot
            try:
                for child in current_process.children(recursive=True):
                    protected_pids.add(child.pid)
                    try:
                        child_exe = child.exe().lower() if child.exe() else ""
                        if child_exe:
                            protected_paths.add(child_exe)
                    except:
                        pass
            except:
                pass
            
            print(f"🛡️ Protegiendo PIDs del bot: {sorted(protected_pids)}")
            
        except Exception as e:
            print(f"⚠️ Error al obtener información del proceso del bot: {e}")
            # Fallback: usar métodos básicos
            current_pid = os.getpid()
            protected_pids.add(current_pid)
            try:
                current_ppid = os.getppid() if hasattr(os, 'getppid') else None
                if current_ppid:
                    protected_pids.add(current_ppid)
            except:
                pass
        
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
                    #print(f"📋 Procesos encontrados para '{variant}':")
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
                                    
                                    # PROTECCIÓN CRÍTICA 1: Verificar PID protegido
                                    if pid in protected_pids:
                                        print(f"🛡️ PROTEGIDO: Omitiendo proceso del bot (PID: {pid})")
                                        continue
                                    
                                    # PROTECCIÓN CRÍTICA 2: Verificar ruta del proceso ANTES de matarlo
                                    proc_path = None
                                    try:
                                        proc_info_cmd = f'powershell "Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path"'
                                        proc_info = subprocess.run(proc_info_cmd, shell=True, capture_output=True, text=True, timeout=3)
                                        if proc_info.returncode == 0 and proc_info.stdout:
                                            proc_path = proc_info.stdout.strip()
                                            proc_path_lower = proc_path.lower()
                                            
                                            # Verificar si la ruta está protegida
                                            is_protected = False
                                            for protected_path in protected_paths:
                                                if protected_path and protected_path in proc_path_lower:
                                                    is_protected = True
                                                    break
                                            
                                            # Verificar si es Python o contiene "ultrabot"
                                            if not is_protected:
                                                if 'python' in proc_path_lower or 'ultrabot' in proc_path_lower:
                                                    is_protected = True
                                            
                                            if is_protected:
                                                print(f"🛡️ PROTEGIDO: Omitiendo proceso del bot (PID: {pid}, Path: {proc_path})")
                                                continue
                                    except Exception as path_error:
                                        # Si no podemos obtener la ruta, NO matar el proceso por seguridad
                                        print(f"⚠️ No se pudo verificar la ruta del proceso {pid}. Por seguridad, NO se matará este proceso.")
                                        continue
                                    
                                    # Si llegamos aquí, el proceso es seguro de matar
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
