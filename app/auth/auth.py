import requests
from app.database.database import save_user, delete_logged_in_user, get_logged_in_user


BASE_API_URL = "http://34.44.12.122/api/auth"

LOGIN_URL = f"{BASE_API_URL}/login"
VERIFY_TOKEN_URL = f"{BASE_API_URL}/verify-token"


def login(username, password):
    payload = {"username": username, "password": password}

    try:
        response = requests.post(LOGIN_URL, json=payload)

        # Intentar decodificar la respuesta JSON
        try:
            response_data = response.json()
        except ValueError:
            # print(f"Error al decodificar la respuesta JSON: {response.text}")
            return {"error": "Error al procesar la respuesta del servidor"}

        # Si la API devuelve un error (401, 403, etc.), devolver ese mensaje
        if response.status_code != 200:
            # print(f"Error de la API: {response.status_code} - {response.text}")
            return response_data  # Devuelve el JSON con el error

        # Si el login es exitoso, almacenar los datos en la base de datos
        if "access_token" in response_data:
            user_data = {
                "id": response_data.get("id"),
                "name": response_data.get("name"),
                "lastname": response_data.get("lastname"),
                "access_token": response_data.get("access_token"),
            }
            save_user(user_data)

            # print(f"Usuario {username} logueado exitosamente.")
            # print(f"Nombre: {user_data['name']} {user_data['lastname']}")
            # print(f"ID: {user_data['id']}")
            return response_data  # Devuelve los datos del usuario

        # Si no tiene un token pero la API respondió correctamente
        return {"error": "Respuesta inesperada del servidor"}

    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return {"error": "Error de conexión con el servidor"}


def logout():

    if delete_logged_in_user():
        # print("Logout exitoso.")
        return True
    else:
        # print("No se pudo cerrar la sesión porque no hay usuario logueado.")
        return False


def verify_token():

    user = get_logged_in_user()  # Obtener el usuario logueado

    if not user:
        # print("No hay usuario logueado para verificar el token.")
        return {"is_valid": False}  # Retornar un diccionario siempre

    access_token = user.get("access_token")
    user_id = user.get("id")

    if not access_token:
        # print("El usuario logueado no tiene un token almacenado.")
        return {"is_valid": False}

    # Hacer la petición a la API de verificación de token
    payload = {"access_token": access_token}
    url = f"{VERIFY_TOKEN_URL}/{user_id}"

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            return response_data  # Devuelve la respuesta de la API
        else:
            # print(f"Error en verificación del token: {response_data}")
            return {"is_valid": False}

    except requests.RequestException as e:
        print(f"Error de conexión al verificar el token: {e}")
        # Asegurar que siempre retorne un diccionario
        return {"is_valid": False}
