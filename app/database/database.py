
import os
import sys
import sqlite3


# Determinar la ubicación base correcta
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Carpeta del ejecutable
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(
        __file__), "..", ".."))  # Subir a la raíz del proyecto

DB_DIR = os.path.join(BASE_DIR, "app", "database")
DB_PATH = os.path.join(DB_DIR, "cookies.db")


def create_database():
    os.makedirs(DB_DIR, exist_ok=True)

    if not os.path.exists(DB_PATH):
        print(f"⚠️ Base de datos no encontrada en {DB_PATH}. Creando una nueva...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 🔹 Crear tabla de cookies
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

        # 🔹 Crear tabla de accounts (con la misma estructura que cookies)
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cookie TEXT NOT NULL,
                email TEXT,
                password TEXT
            )
            '''
        )

        # 🔹 Crear tabla de usuario
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,  
                name TEXT NOT NULL,      
                lastname TEXT NOT NULL,  
                access_token TEXT NOT NULL 
            )
            '''
        )

        # 🔹 Crear tabla para configuraciones del bot
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS bot_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iterations INTEGER NOT NULL,
                interval_seconds INTEGER NOT NULL
            )
            '''
        )

        # 🔹 Crear tabla para guardar credenciales de Ultra
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS ultra_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
            '''
        )

        conn.commit()
        conn.close()
        print(f"✅ Base de datos lista en {DB_PATH}")

    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")

#! FUNCIONES DE USERS
def save_user(user_data):

    try:
        conn = sqlite3.connect(DB_PATH)  # Usar ruta fija
        cursor = conn.cursor()

        # Insertar o reemplazar el usuario en la tabla
        cursor.execute(
            '''
            INSERT OR REPLACE INTO user (id, name, lastname, access_token)
            VALUES (?, ?, ?, ?)
            ''',
            (user_data["id"], user_data["name"],
             user_data["lastname"], user_data["access_token"])
        )

        conn.commit()
        # print(f"Usuario {user_data['name']} {
        #   user_data['lastname']} guardado exitosamente.")
    except sqlite3.IntegrityError as e:
        print(f"Error: No se pudo guardar el usuario. Detalles: {e}")
    finally:
        conn.close()


def get_logged_in_user():

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener al primer usuario registrado en la tabla `user`
        cursor.execute(
            "SELECT id, name, lastname, access_token FROM user LIMIT 1")
        user = cursor.fetchone()

        if user:
            user_data = {
                "id": user[0],
                "name": user[1],
                "lastname": user[2],
                "access_token": user[3]
            }
            return user_data
        else:
            # print("No hay ningún usuario logueado en la base de datos.")
            return None

    except sqlite3.Error as e:
        print(f"Error al obtener el usuario logueado: {e}")
        return None
    finally:
        conn.close()


def delete_logged_in_user():

    user = get_logged_in_user()

    if not user:
        print("No hay ningún usuario logueado para eliminar.")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Eliminar el usuario por su ID
        cursor.execute("DELETE FROM user WHERE id = ?", (user["id"],))
        conn.commit()
        # print(f"Usuario {user['name']} {user['lastname']} eliminado exitosamente de la base de datos.")
        return True

    except sqlite3.Error as e:
        print(f"Error al eliminar el usuario: {e}")
        return False
    finally:
        conn.close()


#! FUNCIONES DE LAS COOKIES
def save_cookies_to_db(cookies):

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
    # print(f"{len(cookies)} cookies guardadas exitosamente en la base de datos.")


def get_cookie_by_id(cookie_id):
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
        # print(f"No se encontró un email asociado con la cookie ID {
        #       cookie_id}.")
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
        # print(f"No se encontró un password asociado con la cookie ID {cookie_id}.")
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

        # print(
        #     f"Base de datos limpiada y reiniciada exitosamente en {DB_PATH}.")
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        conn.close()




def save_bot_settings(iterations, interval_seconds):
    """Guarda o actualiza la configuración del bot."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificamos si ya hay una configuración guardada
        cursor.execute("SELECT id FROM bot_settings LIMIT 1")
        existing = cursor.fetchone()

        if existing:
            # Si existe, actualizamos
            cursor.execute('''
                UPDATE bot_settings
                SET iterations = ?, interval_seconds = ?
                WHERE id = ?
            ''', (iterations, interval_seconds, existing[0]))
        else:
            # Si no existe, insertamos nueva
            cursor.execute('''
                INSERT INTO bot_settings (iterations, interval_seconds)
                VALUES (?, ?)
            ''', (iterations, interval_seconds))

        conn.commit()
        conn.close()
        print("✅ Configuración guardada correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False


def get_bot_settings():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT iterations, interval_seconds FROM bot_settings LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"iterations": row[0], "interval_seconds": row[1]}
        else:
            return None
    except Exception as e:
        print(f"❌ Error al obtener configuración: {e}")
        return None

def save_ultra_credentials(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Si ya existe una fila, la actualiza. Si no, inserta nueva.
        cursor.execute("SELECT id FROM ultra_credentials LIMIT 1")
        if cursor.fetchone():
            cursor.execute(
                "UPDATE ultra_credentials SET email = ?, password = ? WHERE id = 1",
                (email, password)
            )
        else:
            cursor.execute(
                "INSERT INTO ultra_credentials (email, password) VALUES (?, ?)",
                (email, password)
            )

        conn.commit()
        conn.close()
        print("✅ Credenciales de Ultra guardadas correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar credenciales: {e}")


def get_ultra_credentials():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email, password FROM ultra_credentials LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"email": row[0], "password": row[1]}
        return None
    except Exception as e:
        print(f"❌ Error al obtener credenciales: {e}")
        return None
