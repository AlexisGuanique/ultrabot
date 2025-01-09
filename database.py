import sqlite3

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
        cursor.execute('INSERT INTO cookies (cookie) VALUES (?)', (cookie,))

    conn.commit()
    conn.close()
    print(f"{len(cookies)} cookies guardadas exitosamente en la base de datos.")
