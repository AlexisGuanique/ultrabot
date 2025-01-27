import sqlite3
import json


def create_database():
    """
    Crea la base de datos y la tabla para almacenar cookies si no existe.
    """
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    # Crear tabla si no existe
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie TEXT NOT NULL,
            email TEXT,
            password TEXT
        )
        '''
    )

    conn.commit()
    conn.close()
    print("Base de datos creada exitosamente.")


def save_cookies_to_db(cookies):
    """
    Guarda cada cookie como un único registro en la base de datos con email y password.
    """
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    for cookie_entry in cookies:
        cursor.execute(
            '''
            INSERT INTO cookies (cookie, email, password) 
            VALUES (?, ?, ?)
            ''',
            (cookie_entry["cookie"], cookie_entry["email"],
             cookie_entry["password"])
        )

    conn.commit()
    conn.close()
    print(f"{len(cookies)} cookies guardadas exitosamente en la base de datos.")


def get_cookie_by_id(cookie_id):
    """
    Obtiene una cookie de la base de datos utilizando su ID.
    Retorna la cookie exactamente como está guardada en la base de datos.
    """
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    # Consultar la cookie por ID
    cursor.execute('SELECT cookie FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        # Retorna la cookie como texto (sin decodificar a Python)
        return result[0]
    else:
        print(f"No se encontró una cookie con ID {cookie_id}.")
        return None


def get_email_by_id(cookie_id):
    """Obtiene el email asociado a una cookie por su ID."""
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No se encontró un email asociado con la cookie ID {
              cookie_id}")
        return None


def get_password_by_id(cookie_id):
    """Obtiene el password asociado a una cookie por su ID."""
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    cursor.execute('SELECT password FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No se encontró un password asociado con la cookie ID {
              cookie_id}.")
        return None


def clear_database():
    """
    Elimina todos los registros de la tabla 'cookies' en la base de datos.
    """
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM cookies')  # Eliminar todos los registros
        conn.commit()
        print("Base de datos limpiada exitosamente.")
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        conn.close()
