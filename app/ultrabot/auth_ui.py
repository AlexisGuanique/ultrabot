import tkinter as tk
from tkinter import messagebox
from app.auth.auth import login

def setup_auth_ui(on_login_success):

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        login_data = login(username, password)  # Recibe el JSON con los datos del usuario

        if login_data and login_data.get("access_token"):
            messagebox.showinfo("Login Exitoso", f"Bienvenido, {login_data.get('name')} {login_data.get('lastname')}!")
            root.destroy()
            on_login_success(login_data)  # Pasa el JSON completo con la información del usuario
        else:
            messagebox.showerror("Login Fallido", "Usuario o contraseña incorrectos.")

    root = tk.Tk()
    root.title("Login - Ultra Bot")
    root.geometry("800x600")

    username_label = tk.Label(root, text="Usuario:", font=("Arial", 12))
    username_label.pack(pady=10)
    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Contraseña:", font=("Arial", 12))
    password_label.pack(pady=10)
    password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(root, text="Iniciar Sesión", command=handle_login, font=("Arial", 12), bg="green", fg="white")
    login_button.pack(pady=20)

    root.mainloop()
