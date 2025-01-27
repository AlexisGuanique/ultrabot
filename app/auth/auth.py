logged_in_user = None  # Variable global para almacenar el usuario logueado

def login(username, password):

    global logged_in_user
    if username and password:
        print(f"Intentando iniciar sesión con:\nUsuario: {username}\nContraseña: {password}")
        logged_in_user = username  # Guarda el usuario como logueado
        print(f"Usuario {username} logueado exitosamente.")
        return True
    else:
        print("Error: Usuario o contraseña vacíos.")
        return False

def logout():

    global logged_in_user
    if logged_in_user:
        print(f"Usuario {logged_in_user} ha cerrado sesión.")
        logged_in_user = None  # Limpia el usuario logueado
        return True
    else:
        print("No hay ningún usuario logueado.")
        return False
