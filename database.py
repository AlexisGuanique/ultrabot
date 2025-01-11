import sqlite3
import json



def create_database():
    """Crea la base de datos y la tabla para almacenar cookies como texto."""
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    # Crear tabla para almacenar las cookies completas como texto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos creada exitosamente.")


def save_cookies_to_db(cookies):
    """Guarda cada cookie como un único registro en la base de datos."""
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    for cookie in cookies:
        # Serializar cada cookie como JSON antes de guardarla
        cookie_json = json.dumps(cookie)
        cursor.execute(
            'INSERT INTO cookies (cookie) VALUES (?)', (cookie_json,))

    conn.commit()
    conn.close()
    print(f"{len(cookies)} cookies guardadas exitosamente en la base de datos.")


def get_cookie_by_id(cookie_id):
    """
    Obtiene una cookie de la base de datos utilizando su ID.
    Retorna el JSON de la cookie decodificado.
    """
    conn = sqlite3.connect('cookies.db')
    cursor = conn.cursor()

    # Consultar la cookie por ID
    cursor.execute('SELECT cookie FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        try:
            # Decodificar la cookie desde JSON
            cookie_data = json.loads(result[0])
            return cookie_data
        except json.JSONDecodeError as e:
            print(f"Error al decodificar la cookie: {e}")
            return None
    else:
        print(f"No se encontró una cookie con ID {cookie_id}.")
        return None
