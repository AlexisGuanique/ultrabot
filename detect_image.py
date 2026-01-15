#!/usr/bin/env python3
"""
Script para detectar imágenes en la pantalla continuamente y dibujar un rectángulo rojo alrededor.
Uso: python detect_image.py <ruta_imagen> [confianza]
Presiona Ctrl+C para detener el script.
"""

import pyautogui
import sys
import os
import time
import tkinter as tk
import threading

def get_resource_path(relative_path):
    """Obtiene el path dinámico de los archivos (igual que en ultra_bot.py)"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_image(image_path, confidence=0.7):
    """
    Busca una imagen en la pantalla y devuelve su ubicación si la encuentra.
    Usa la misma función que ultra_bot.py
    """
    image_path = get_resource_path(image_path)
    try:
        if not os.path.exists(image_path):
            return None

        # Usar locateOnScreen para obtener el rectángulo completo (left, top, width, height)
        location = pyautogui.locateOnScreen(
            image_path, confidence=confidence, grayscale=True)
        if location:
            return location

    except Exception as e:
        pass
    return None

def draw_rectangle_overlay(location):
    """
    Dibuja un rectángulo rojo alrededor de la imagen encontrada usando una ventana overlay.
    
    Args:
        location: Tupla (left, top, width, height) de la ubicación de la imagen
    """
    if not location:
        return
    
    left, top, width, height = location
    padding = 5
    
    # Crear ventana transparente
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.9)
    root.configure(bg='black')
    
    # Posicionar la ventana
    root.geometry(f'{width + padding * 2}x{height + padding * 2}+{left - padding}+{top - padding}')
    
    # Crear canvas para dibujar
    canvas = tk.Canvas(
        root, 
        highlightthickness=0, 
        bg='black',
        width=width + padding * 2,
        height=height + padding * 2
    )
    canvas.pack()
    
    # Dibujar rectángulo rojo
    canvas.create_rectangle(
        padding, padding, width + padding, height + padding,
        outline='red', width=3
    )
    
    # Mostrar la ventana por 2 segundos
    root.after(2000, root.destroy)
    root.mainloop()

def monitor_image(image_path, confidence=0.7, interval=0.5):
    """
    Monitorea continuamente la pantalla buscando la imagen.
    
    Args:
        image_path: Ruta a la imagen a buscar
        confidence: Nivel de confianza (0.0 a 1.0)
        interval: Intervalo entre búsquedas en segundos
    """
    last_found = False
    image_path_resolved = get_resource_path(image_path)
    
    print(f"🔍 Monitoreando imagen: {image_path}")
    print(f"📊 Nivel de confianza: {confidence}")
    print(f"⏱️  Intervalo de búsqueda: {interval} segundos")
    print("🔄 Escaneando pantalla continuamente...")
    print("💡 Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            location = find_image(image_path, confidence)
            
            if location:
                left, top, width, height = location
                if not last_found:
                    # Solo mostrar mensaje cuando se detecta por primera vez o después de no estar
                    print(f"✅ Imagen encontrada! Ubicación: ({left}, {top}) Tamaño: {width}x{height}")
                    last_found = True
                
                # Dibujar rectángulo en un hilo separado para no bloquear
                threading.Thread(target=draw_rectangle_overlay, args=(location,), daemon=True).start()
            else:
                if last_found:
                    print("❌ Imagen ya no visible")
                    last_found = False
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo monitoreo...")
        print("✅ Script finalizado.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python detect_image.py <ruta_imagen> [confianza] [intervalo]")
        print("Ejemplo: python detect_image.py app/ultrabot/images/ultraLogo/ultraLogo.png 0.8 0.5")
        print("\nParámetros:")
        print("  ruta_imagen: Ruta a la imagen a buscar")
        print("  confianza:   Nivel de confianza (0.0 a 1.0, default: 0.7)")
        print("  intervalo:   Segundos entre búsquedas (default: 0.5)")
        sys.exit(1)
    
    image_path = sys.argv[1]
    confidence = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    
    # Verificar que la imagen existe
    resolved_path = get_resource_path(image_path)
    if not os.path.exists(resolved_path):
        print(f"❌ Error: La imagen no existe: {resolved_path}")
        sys.exit(1)
    
    monitor_image(image_path, confidence, interval)

if __name__ == "__main__":
    main()
