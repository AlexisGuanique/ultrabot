
import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'cookies.db')


def create_database():
    """
    Crea la base de datos y la tabla para almacenar cookies si no existe.
    """
    conn = sqlite3.connect(DB_PATH)  # Usar ruta fija
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
    print(f"Base de datos creada exitosamente en {DB_PATH}.")


def save_cookies_to_db(cookies):
    """
    Guarda cada cookie como un único registro en la base de datos con email y password.
    """
    conn = sqlite3.connect(DB_PATH)
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
    """Obtiene una cookie por su ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT cookie FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No se encontró una cookie con ID {cookie_id}.")
        return None


def get_email_by_id(cookie_id):
    """Obtiene el email asociado a una cookie por su ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No se encontró un email asociado con la cookie ID {
              cookie_id}.")
        return None


def get_password_by_id(cookie_id):
    """Obtiene el password asociado a una cookie por su ID."""
    conn = sqlite3.connect(DB_PATH)
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


def get_cookie_count():
    """Obtiene la cantidad de cookies almacenadas en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM cookies")
        count = cursor.fetchone()[0]
        return count
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()


def clear_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Eliminar la tabla 'cookies' si existe
        cursor.execute('DROP TABLE IF EXISTS cookies')
        conn.commit()

        # Crear la tabla nuevamente
        cursor.execute('''
            CREATE TABLE cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cookie TEXT NOT NULL,
                email TEXT,
                password TEXT
            )
        ''')
        conn.commit()

        print(
            f"Base de datos limpiada y reiniciada exitosamente en {DB_PATH}.")
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        conn.close()
