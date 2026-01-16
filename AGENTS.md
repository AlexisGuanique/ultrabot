# AGENTS.md - Development Guidelines for UltraBot

## Overview
UltraBot is a Python desktop application for cookie management and automation, built with CustomTkinter, SQLite, and computer vision capabilities using PyAutoGUI and OpenCV.

## Build Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Production Builds

#### Windows Build (Personal Machine)
```bash
pyinstaller --onefile --windowed --icon="C:/Users/Usuario/workspace/ultra/ultrabot/favicon.ico" --name=UltraBot-Automation-v2-login --add-data "app/ultrabot/images:app/ultrabot/images" main.py
```

#### Windows Build (VPS - Debug Version)
```bash
pyinstaller --onefile --icon="C:/Users/Administrator/workspace/ultrabot/favicon.ico" --name=UltraBot-AllAutomation-Debug --add-data "app/ultrabot/images:app/ultrabot/images" main.py
```

#### Windows Build (VPS - Production Version)
```bash
pyinstaller --onefile --windowed --icon="C:/Users/Administrator/workspace/ultrabot/favicon.ico" --name=UltraBot-AllAutomation --add-data "app/ultrabot/images:app/ultrabot/images" main.py
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Testing Commands

Currently, no automated test suite is configured. Manual testing is performed by:

1. Running the application: `python main.py`
2. Testing cookie import functionality with sample .txt files
3. Verifying database operations (SQLite browser recommended)
4. Testing GUI interactions manually

### Recommended Test Setup (Future Implementation)
```bash
# Install testing dependencies (add to requirements.txt)
pip install pytest pytest-cov

# Run tests (when implemented)
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Code Style Guidelines

### Language and Framework
- **Language**: Python 3.7+
- **GUI Framework**: CustomTkinter (modern Tkinter wrapper)
- **Database**: SQLite3
- **Automation**: PyAutoGUI with OpenCV for image recognition
- **Packaging**: PyInstaller for executable builds

### Import Organization
```python
# Standard library imports first
import os
import sys
import sqlite3
import threading
import json

# Third-party imports second
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import pyautogui
import cv2
import requests
from PIL import ImageGrab

# Local imports last (relative imports)
from app.database.database import create_database, get_cookie_count
from app.ultrabot.ui import setup_ui
from app.auth.auth import verify_token
```

### Naming Conventions

#### Variables and Functions
- Use `snake_case` for variables and functions
- Be descriptive but concise
- Use Spanish for user-facing strings (UI labels, messages)
- Use English for code comments and internal naming

```python
# Good
def update_cookie_count():
    total_cookies = get_cookie_count()

# Avoid
def updateCookieCount():
    totalcookies = get_cookie_count()
```

#### Constants
- Use `UPPER_SNAKE_CASE` for constants
- Define at module level

```python
DB_PATH = os.path.join(BASE_DIR, "app", "database", "cookies.db")
DEFAULT_CONFIDENCE = 0.7
```

#### Classes
- Use `PascalCase` for class names
- Keep classes focused on single responsibilities

### Code Structure

#### Function Organization
- Functions should be small and focused (ideally < 50 lines)
- Use descriptive names that indicate purpose
- Include docstrings for complex functions

```python
def find_image(image_path, confidence=0.7):
    """Busca una imagen en la pantalla y devuelve su ubicación si la encuentra."""
    # Implementation here
```

#### Error Handling
- Use try/except blocks for operations that may fail
- Show user-friendly error messages via messagebox
- Log technical details for debugging

```python
try:
    clear_database()
    update_cookie_count()
    messagebox.showinfo("Éxito", "Cookies limpiadas correctamente.")
except Exception as e:
    messagebox.showerror("Error", f"Error al limpiar base de datos: {e}")
```

#### File Structure
```
ultrabot/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── app/
│   ├── ultrabot/             # Main application logic
│   │   ├── ui.py            # Main GUI setup
│   │   ├── auth_ui.py       # Authentication UI
│   │   ├── ultra_bot.py     # Automation logic
│   │   ├── file_handler.py  # File processing
│   │   ├── utils_ultrabot.py # Utility functions
│   │   └── images/          # UI assets
│   ├── database/            # Database operations
│   │   └── database.py
│   ├── auth/                # Authentication
│   │   └── auth.py
│   └── code/                # Business logic
│       ├── profile_config.py
│       ├── hostinger_login.py
│       └── hostinger_actions.py
```

### GUI Development

#### CustomTkinter Patterns
- Use `ctk.CTk*` widgets instead of standard tkinter
- Set consistent theming (colors, fonts)
- Use English for widget names, Spanish for display text

```python
# Good
login_button = ctk.CTkButton(
    master=frame,
    text="Iniciar Sesión",  # Spanish for user display
    command=login_function
)

# Consistent styling
login_button.configure(
    fg_color="blue",
    text_color="white",
    font=("Arial", 12, "bold")
)
```

#### Layout Management
- Use `pack()`, `grid()`, or `place()` consistently within a file
- Prefer `grid()` for complex layouts
- Group related widgets in frames

### Database Operations

#### SQLite Patterns
- Use parameterized queries to prevent SQL injection
- Handle connection opening/closing properly
- Include error handling for database operations

```python
def save_cookies_to_db(cookie_data):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO cookies (cookie, email, password) VALUES (?, ?, ?)",
            (cookie_data['cookie'], cookie_data['email'], cookie_data['password'])
        )

        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
```

### Automation Code

#### PyAutoGUI Usage
- Always set `pyautogui.FAILSAFE = False` for production
- Use image recognition over coordinate clicking when possible
- Include confidence levels and error handling

```python
def find_image(image_path, confidence=0.7):
    """Busca una imagen en la pantalla."""
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path,
            confidence=confidence,
            grayscale=True
        )
        if location:
            print(f"✅ Imagen detectada: {image_path}")
            return location
        else:
            print(f"❌ Imagen no encontrada: {image_path}")
            return None
    except Exception as e:
        print(f"⚠️ Error buscando imagen: {e}")
        return None
```

### Security Considerations
- Never log sensitive information (passwords, tokens)
- Use secure token verification
- Validate user inputs
- Handle authentication securely

### Documentation
- Use Spanish for user documentation and comments
- Include docstrings for all public functions
- Keep README updated with build instructions

### Code Quality Tools (Recommended Setup)

Add these to `requirements-dev.txt`:
```bash
# Linting and formatting
pip install flake8 black isort ruff

# Run linting
ruff check .

# Format code
black .

# Sort imports
isort .
```

### Git Workflow
- Use descriptive commit messages in Spanish
- Test builds before committing
- Include version numbers in build names
- Keep sensitive data out of repository

---

## Quick Reference

### Running the Application
```bash
python main.py
```

### Building for Distribution
```bash
pyinstaller --onefile --windowed --icon="favicon.ico" --name=UltraBot --add-data "app/ultrabot/images:app/ultrabot/images" main.py
```

### Database Inspection
```bash
sqlite3 app/database/cookies.db
.schema
SELECT * FROM cookies LIMIT 5;
```

### Key Dependencies
- `customtkinter`: Modern GUI framework
- `pyautogui`: Screen automation
- `opencv-python`: Image processing
- `sqlite3`: Database (built-in)
- `pillow`: Image handling
- `requests`: HTTP client</content>
<parameter name="filePath">/Users/josephperez/Projects/ultrabot/AGENTS.md