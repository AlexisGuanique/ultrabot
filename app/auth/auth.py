import requests
from app.database.database import save_user, delete_logged_in_user


API_URL = "http://34.44.12.122/api/auth/login"
# Declarar las variables globales


def login(username, password):
    payload = {"username": username, "password": password}

    try:
        response = requests.post(API_URL, json=payload)

        # Registrar la respuesta completa en caso de error
        if response.status_code != 200:
            print(f"Error de la API: {response.status_code} - {response.text}")
            return None

        # Intentar decodificar el JSON
        try:
            response_data = response.json()
        except ValueError:
            print(f"Error al decodificar la respuesta JSON: {response.text}")
            return None

        if "access_token" in response_data:
            # Almacenar los datos del usuario en la base de datos
            user_data = {
                "id": response_data.get("id"),
                "name": response_data.get("name"),
                "lastname": response_data.get("lastname"),
                "access_token": response_data.get("access_token"),
            }
            save_user(user_data)

            print(f"Usuario {username} logueado exitosamente.")
            print(f"Nombre: {user_data['name']} {user_data['lastname']}")
            print(f"ID: {user_data['id']}")
            return response_data
        else:
            print(f"Error en login: {response_data.get(
                'message', 'Error desconocido')}")
            return None

    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def logout():
    """
    Cierra sesión del usuario logueado eliminándolo de la base de datos.

    :return: True si se cerró la sesión correctamente, False si no había usuario logueado.
    """
    if delete_logged_in_user():
        print("Logout exitoso.")
        return True
    else:
        print("No se pudo cerrar la sesión porque no hay usuario logueado.")
        return False
