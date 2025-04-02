import threading
import pyperclip
import pyautogui
import time
from app.database.database import get_cookie_by_id, get_password_by_id, get_bot_settings
import cv2
import os
import sys
from PIL import ImageGrab
from tkinter import messagebox

def get_resource_path(relative_path):

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Funcion para arreglas la imagen antes de buscarla


def find_image(image_path, confidence=0.7):
    """Busca una imagen en la pantalla y devuelve su ubicación si la encuentra."""
    image_path = get_resource_path(image_path)
    try:
        if not os.path.exists(image_path):
            print(f"⚠️ La imagen no existe: {image_path}")
            return None

        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, grayscale=True)
        if location:
            print(f"✅ Imagen detectada: {image_path} en {location}")
            return location
        else:
            print(f"❌ Imagen no encontrada: {image_path}")

    except Exception as e:
        print(f"⚠️ Error detectando {image_path}: {e}")
    return None