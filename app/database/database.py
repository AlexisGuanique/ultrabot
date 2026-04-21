
import os
import sys
import sqlite3
import requests
import json
from app.config.server import (
    ACCOUNTS_NEXT_URL_TEMPLATE,
    ACCOUNTS_COUNT_URL_TEMPLATE,
)


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
                password TEXT,
                user_agent TEXT
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
                interval_seconds INTEGER NOT NULL,
                user_agent TEXT DEFAULT ''
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

        # 🔹 Crear tabla para guardar credenciales de Hostinger
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS hostinger_credentials (
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
    
    # Ejecutar migraciones para asegurar que todas las tablas estén actualizadas
    run_migrations()


def run_migrations():
    """
    Ejecuta migraciones para agregar nuevas tablas o columnas a la base de datos existente.
    Esta función se ejecuta después de create_database() para asegurar compatibilidad con bases de datos antiguas.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Migración: Agregar tabla repetidas_settings si no existe
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='repetidas_settings'
        ''')
        
        if not cursor.fetchone():
            print("🔄 Ejecutando migración: Creando tabla repetidas_settings...")
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS repetidas_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    accounts_to_repeat INTEGER NOT NULL,
                    repetitions_count INTEGER NOT NULL,
                    interval_seconds INTEGER NOT NULL
                )
                '''
            )
            conn.commit()
            print("✅ Migración completada: Tabla repetidas_settings creada exitosamente.")
        else:
            print("✅ Tabla repetidas_settings ya existe, omitiendo migración.")

        # Migración: Agregar columna partitions_count a repetidas_settings si no existe
        cursor.execute("PRAGMA table_info(repetidas_settings)")
        repetidas_columns = [col[1] for col in cursor.fetchall()]
        if 'partitions_count' not in repetidas_columns:
            print("🔄 Ejecutando migración: Agregando columna partitions_count a repetidas_settings...")
            cursor.execute("ALTER TABLE repetidas_settings ADD COLUMN partitions_count INTEGER NOT NULL DEFAULT 1")
            conn.commit()
            print("✅ Migración completada: columna partitions_count agregada.")

        # Migración: Agregar columnas bot_name y bot_type a bot_settings si no existen
        cursor.execute("PRAGMA table_info(bot_settings)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        if 'bot_name' not in existing_columns:
            print("🔄 Ejecutando migración: Agregando columna bot_name a bot_settings...")
            try:
                cursor.execute("ALTER TABLE bot_settings ADD COLUMN bot_name TEXT DEFAULT 'Mi Bot 1'")
                conn.commit()
                print("✅ Migración bot_name aplicada exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migración bot_name: {e}")
        
        if 'bot_type' not in existing_columns:
            print("🔄 Ejecutando migración: Agregando columna bot_type a bot_settings...")
            try:
                cursor.execute("ALTER TABLE bot_settings ADD COLUMN bot_type TEXT DEFAULT 'logueador'")
                conn.commit()
                print("✅ Migración bot_type aplicada exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migración bot_type: {e}")

        if 'user_agent' not in existing_columns:
            print("🔄 Ejecutando migración: Agregando columna user_agent a bot_settings...")
            try:
                cursor.execute("ALTER TABLE bot_settings ADD COLUMN user_agent TEXT DEFAULT ''")
                conn.commit()
                print("✅ Migración user_agent aplicada exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migración user_agent: {e}")

        cursor.execute("PRAGMA table_info(bot_settings)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        if 'ultra_login_mode' not in existing_columns:
            print("🔄 Ejecutando migración: Agregando columna ultra_login_mode a bot_settings...")
            try:
                cursor.execute(
                    "ALTER TABLE bot_settings ADD COLUMN ultra_login_mode TEXT DEFAULT 'sqlite'"
                )
                conn.commit()
                print("✅ Migración ultra_login_mode aplicada exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migración ultra_login_mode: {e}")

        cursor.execute("PRAGMA table_info(bot_settings)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        if "run_repetidas" not in existing_columns:
            print("🔄 Ejecutando migración: Agregando columna run_repetidas a bot_settings...")
            try:
                cursor.execute(
                    "ALTER TABLE bot_settings ADD COLUMN run_repetidas INTEGER DEFAULT 0"
                )
                conn.commit()
                print("✅ Migración run_repetidas aplicada exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migración run_repetidas: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al ejecutar migraciones: {e}")


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
            INSERT INTO cookies (cookie, email, password, user_agent) 
            VALUES (?, ?, ?, ?)
            ''',
            (
                cookie_entry["cookie"],
                cookie_entry["email"],
                cookie_entry["password"],
                cookie_entry.get("user_agent", None)
            )
        )

    conn.commit()
    conn.close()


def get_user_agent_by_id(cookie_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT user_agent FROM cookies WHERE id = ?', (cookie_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print(f"No se encontró un user agent para el ID {cookie_id}.")
        return None



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


def get_all_cookie_records():
    """
    Obtiene todas las filas de la tabla cookies (p. ej. para conversión a SQLite de Chrome).

    Returns:
        Lista de dicts con keys: id, cookie, email, password, user_agent.
        Orden por id ascendente. Lista vacía si error o tabla inexistente.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, cookie, email, password, user_agent FROM cookies ORDER BY id"
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "cookie": row[1],
                "email": row[2],
                "password": row[3],
                "user_agent": row[4],
            }
            for row in rows
        ]
    except sqlite3.OperationalError:
        return []
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
                password TEXT,
                user_agent TEXT
            )
        ''')
        conn.commit()

        # print(
        #     f"Base de datos limpiada y reiniciada exitosamente en {DB_PATH}.")
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        conn.close()


def snapshot_cookie_rows_ordered():
    """
    Filas actuales de cookies como tuplas (cookie, email, password, user_agent)
    en orden ORDER BY id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT cookie, email, password, user_agent FROM cookies ORDER BY id"
        )
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def replace_cookies_table_rows(rows):
    """
    Sustituye por completo el contenido de la tabla cookies por estas filas
    (nuevos ids autoincrement). rows: lista de tuplas (cookie, email, password, user_agent).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cookies")
        for r in rows:
            cursor.execute(
                """
                INSERT INTO cookies (cookie, email, password, user_agent)
                VALUES (?, ?, ?, ?)
                """,
                r,
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en replace_cookies_table_rows: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def truncate_cookies_to_first_n(n: int) -> bool:
    """Deja solo las primeras n filas (ORDER BY id). Útil si hay más cuentas locales de las pedidas."""
    if n < 1:
        return False
    rows = snapshot_cookie_rows_ordered()
    if len(rows) <= n:
        return True
    return replace_cookies_table_rows(rows[:n])


def expand_cookies_in_db_for_repetidas(repetitions_count: int) -> bool:
    """
    Por cada fila actual (ORDER BY id), inserta repetitions_count copias con el mismo
    cookie/email/password/user_agent, de modo que BD y Partitions queden alineadas
    (cuentas × repeticiones = pestañas).
    """
    if repetitions_count < 1:
        repetitions_count = 1
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT cookie, email, password, user_agent FROM cookies ORDER BY id"
        )
        rows = cursor.fetchall()
        if not rows:
            print("⚠️ expand_cookies_in_db_for_repetidas: no hay filas en cookies.")
            return False
        cursor.execute("DELETE FROM cookies")
        for row in rows:
            for _ in range(repetitions_count):
                cursor.execute(
                    """
                    INSERT INTO cookies (cookie, email, password, user_agent)
                    VALUES (?, ?, ?, ?)
                    """,
                    row,
                )
        conn.commit()
        n0, n1 = len(rows), len(rows) * repetitions_count
        print(
            f"✅ Repetidas (BD): cada cuenta base duplicada {repetitions_count} vez(ces) "
            f"— {n0} → {n1} filas."
        )
        return True
    except Exception as e:
        print(f"❌ Error en expand_cookies_in_db_for_repetidas: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def save_bot_settings(iterations, interval_seconds, user_agent=""):
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
                SET iterations = ?, interval_seconds = ?, user_agent = ?
                WHERE id = ?
            ''', (iterations, interval_seconds, user_agent, existing[0]))
        else:
            # Si no existe, insertamos nueva
            cursor.execute('''
                INSERT INTO bot_settings (iterations, interval_seconds, user_agent)
                VALUES (?, ?, ?)
            ''', (iterations, interval_seconds, user_agent))

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
        # Obtener todas las columnas disponibles
        cursor.execute("PRAGMA table_info(bot_settings)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Construir SELECT dinámico según las columnas disponibles
        select_fields = ["iterations", "interval_seconds"]
        if 'bot_name' in column_names:
            select_fields.append("bot_name")
        if 'bot_type' in column_names:
            select_fields.append("bot_type")
        if 'use_local_accounts' in column_names:
            select_fields.append("use_local_accounts")
        if 'user_agent' in column_names:
            select_fields.append("user_agent")
        if 'ultra_login_mode' in column_names:
            select_fields.append("ultra_login_mode")
        if 'run_repetidas' in column_names:
            select_fields.append("run_repetidas")
        
        query = f"SELECT {', '.join(select_fields)} FROM bot_settings LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            result = {
                "iterations": row[0], 
                "interval_seconds": row[1]
            }
            idx = 2
            if 'bot_name' in column_names and idx < len(row):
                result["bot_name"] = row[idx]
                idx += 1
            if 'bot_type' in column_names and idx < len(row):
                result["bot_type"] = row[idx]
                idx += 1
            if 'use_local_accounts' in column_names and idx < len(row):
                result["use_local_accounts"] = bool(row[idx])
                idx += 1
            if 'user_agent' in column_names and idx < len(row):
                result["user_agent"] = row[idx] if row[idx] is not None else ""
                idx += 1
            if 'ultra_login_mode' in column_names and idx < len(row):
                result["ultra_login_mode"] = row[idx] if row[idx] is not None else "sqlite"
                idx += 1
            if 'run_repetidas' in column_names and idx < len(row):
                result["run_repetidas"] = bool(row[idx])
            
            conn.close()
            return result
        
        conn.close()
        return None
    except Exception as e:
        print(f"❌ Error al obtener configuración: {e}")
        return None


def save_repetidas_settings(accounts_to_repeat, repetitions_count, interval_seconds, partitions_count=1):
    """Guarda o actualiza la configuración de repetidas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM repetidas_settings LIMIT 1")
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE repetidas_settings
                SET accounts_to_repeat = ?, repetitions_count = ?, interval_seconds = ?, partitions_count = ?
                WHERE id = ?
            ''', (accounts_to_repeat, repetitions_count, interval_seconds, partitions_count, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO repetidas_settings (accounts_to_repeat, repetitions_count, interval_seconds, partitions_count)
                VALUES (?, ?, ?, ?)
            ''', (accounts_to_repeat, repetitions_count, interval_seconds, partitions_count))

        conn.commit()
        conn.close()
        print("✅ Configuración de repetidas guardada correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al guardar configuración de repetidas: {e}")
        return False


def get_repetidas_settings():
    """Obtiene la configuración de repetidas guardada."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT accounts_to_repeat, repetitions_count, interval_seconds, partitions_count FROM repetidas_settings LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "accounts_to_repeat": row[0],
                "repetitions_count": row[1],
                "interval_seconds": row[2],
                "partitions_count": row[3] if row[3] is not None else 1,
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error al obtener configuración de repetidas: {e}")
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


def save_hostinger_credentials(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Si ya existe una fila, la actualiza. Si no, inserta nueva.
        cursor.execute("SELECT id FROM hostinger_credentials LIMIT 1")
        if cursor.fetchone():
            cursor.execute(
                "UPDATE hostinger_credentials SET email = ?, password = ? WHERE id = 1",
                (email, password)
            )
        else:
            cursor.execute(
                "INSERT INTO hostinger_credentials (email, password) VALUES (?, ?)",
                (email, password)
            )

        conn.commit()
        conn.close()
        print("✅ Credenciales de Hostinger guardadas correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar credenciales de Hostinger: {e}")

def get_hostinger_credentials():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email, password FROM hostinger_credentials LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"email": row[0], "password": row[1]}
        return None
    except Exception as e:
        print(f"❌ Error al obtener credenciales de Hostinger: {e}")
        return None


def fetch_accounts_from_server(count):
    """
    Obtiene cuentas del servidor usando las credenciales del usuario logueado.
    
    Args:
        count (int): Número de cuentas a solicitar
        
    Returns:
        list: Lista de cuentas obtenidas del servidor, o None si hay error
    """
    try:
        # Obtener credenciales del usuario logueado
        user = get_logged_in_user()
        if not user:
            print("❌ No hay usuario logueado. No se pueden obtener cuentas del servidor.")
            return None
            
        user_id = user.get("id")
        access_token = user.get("access_token")
        
        if not user_id or not access_token:
            print("❌ Faltan credenciales del usuario (ID o access_token).")
            return None
        
        # URL del endpoint
        url = ACCOUNTS_NEXT_URL_TEMPLATE.format(user_id=user_id)
        
        # Payload de la petición
        payload = {
            "access_token": access_token,
            "count": count
        }
        
        print(f"🌐 Solicitando {count} cuentas del servidor...")
        print(f"📡 URL: {url}")
        
        # Hacer la petición POST
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('accounts', [])
            
            # 🔄 Convertir el array de cookies a cadena JSON
            for account in accounts:
                if 'cookie' in account and isinstance(account['cookie'], list):
                    # Convertir el array de cookies a una cadena JSON
                    account['cookie'] = json.dumps(account['cookie'])
            
            print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
            return accounts
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Detalles del error: {error_data}")
            except:
                print(f"📄 Respuesta del servidor: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión al obtener cuentas del servidor: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al obtener cuentas: {e}")
        return None


def get_server_account_count():
    """
    Obtiene el número de cuentas disponibles en el servidor.
    
    Returns:
        int: Número de cuentas en el servidor, o None si hay error
    """
    try:
        # Obtener credenciales del usuario logueado
        user = get_logged_in_user()
        if not user:
            print("❌ No hay usuario logueado. No se puede obtener el conteo del servidor.")
            return None
            
        user_id = user.get("id")
        access_token = user.get("access_token")
        
        if not user_id or not access_token:
            print("❌ Faltan credenciales del usuario (ID o access_token).")
            return None
        
        # URL del endpoint
        url = ACCOUNTS_COUNT_URL_TEMPLATE.format(user_id=user_id)
        
        # Payload de la petición
        payload = {
            "access_token": access_token
        }
        
        print(f"🌐 Obteniendo conteo de cuentas del servidor...")
        print(f"📡 URL: {url}")
        
        # Hacer la petición POST
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            account_count = data.get('account_count', 0)
            print(f"✅ Conteo del servidor: {account_count} cuentas")
            return account_count
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Detalles del error: {error_data}")
            except:
                print(f"📄 Respuesta del servidor: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión al obtener conteo del servidor: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al obtener conteo: {e}")
        return None


def save_bot_connection_config(bot_name, bot_type='logueador'):
    """Guarda la configuración de conexión del bot (nombre y tipo)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM bot_settings LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE bot_settings
                SET bot_name = ?, bot_type = ?
                WHERE id = ?
            ''', (bot_name, bot_type, existing[0]))
        else:
            # Si no existe configuración, crear una con valores por defecto
            cursor.execute('''
                INSERT INTO bot_settings (iterations, interval_seconds, bot_name, bot_type, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (1, 20, bot_name, bot_type, ""))
        
        conn.commit()
        conn.close()
        print(f"✅ Configuración de conexión guardada: {bot_name} ({bot_type})")
        return True
    except Exception as e:
        print(f"❌ Error al guardar configuración de conexión: {e}")
        return False

def get_bot_connection_config():
    """Obtiene la configuración de conexión del bot (nombre y tipo)
    Nota: Este bot siempre es de tipo 'logueador'"""
    settings = get_bot_settings()
    if settings:
        return {
            "bot_name": settings.get("bot_name", "Mi Bot 1"),
            "bot_type": "logueador"  # Siempre es logueador para este bot
        }
    return {
        "bot_name": "Mi Bot 1",
        "bot_type": "logueador"  # Siempre es logueador para este bot
    }

def save_use_local_accounts(use_local):
    """Guarda la preferencia de usar cuentas locales"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si existe la columna use_local_accounts
        cursor.execute("PRAGMA table_info(bot_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'use_local_accounts' not in columns:
            cursor.execute("ALTER TABLE bot_settings ADD COLUMN use_local_accounts INTEGER DEFAULT 0")
        
        cursor.execute("SELECT id FROM bot_settings LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE bot_settings
                SET use_local_accounts = ?
                WHERE id = ?
            ''', (1 if use_local else 0, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO bot_settings (iterations, interval_seconds, use_local_accounts, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (1, 20, 1 if use_local else 0, ""))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al guardar preferencia de cuentas locales: {e}")
        return False

def get_use_local_accounts():
    """Obtiene la preferencia de usar cuentas locales (por defecto False)"""
    try:
        settings = get_bot_settings()
        if settings and 'use_local_accounts' in settings:
            return bool(settings.get('use_local_accounts', 0))
        return False
    except Exception as e:
        print(f"⚠️  Error al obtener preferencia de cuentas locales: {e}")
        return False


def save_ultra_login_mode(mode: str):
    """Guarda el modo de logueo del Ultra Bot: 'sqlite' o 'ui'."""
    mode = "ui" if mode == "ui" else "sqlite"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bot_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        if "ultra_login_mode" not in columns:
            cursor.execute(
                "ALTER TABLE bot_settings ADD COLUMN ultra_login_mode TEXT DEFAULT 'sqlite'"
            )
        cursor.execute("SELECT id FROM bot_settings LIMIT 1")
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """
                UPDATE bot_settings
                SET ultra_login_mode = ?
                WHERE id = ?
                """,
                (mode, existing[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO bot_settings (iterations, interval_seconds, ultra_login_mode, user_agent)
                VALUES (?, ?, ?, ?)
                """,
                (1, 20, mode, ""),
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al guardar ultra_login_mode: {e}")
        return False


def get_ultra_login_mode():
    """Devuelve 'sqlite' o 'ui' según la preferencia guardada (por defecto 'sqlite')."""
    try:
        settings = get_bot_settings()
        if settings and settings.get("ultra_login_mode"):
            m = settings.get("ultra_login_mode")
            return "ui" if m == "ui" else "sqlite"
        return "sqlite"
    except Exception as e:
        print(f"⚠️  Error al obtener ultra_login_mode: {e}")
        return "sqlite"


def save_run_repetidas_mode(enabled: bool):
    """Si True, Ejecutar Ultra Bot usará el flujo de cuentas repetidas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bot_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        if "run_repetidas" not in columns:
            cursor.execute(
                "ALTER TABLE bot_settings ADD COLUMN run_repetidas INTEGER DEFAULT 0"
            )
        cursor.execute("SELECT id FROM bot_settings LIMIT 1")
        existing = cursor.fetchone()
        val = 1 if enabled else 0
        if existing:
            cursor.execute(
                """
                UPDATE bot_settings
                SET run_repetidas = ?
                WHERE id = ?
                """,
                (val, existing[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO bot_settings (iterations, interval_seconds, run_repetidas, user_agent)
                VALUES (?, ?, ?, ?)
                """,
                (1, 20, val, ""),
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al guardar run_repetidas: {e}")
        return False


def get_run_repetidas_mode():
    """True si el siguiente inicio debe usar el flujo de cuentas repetidas."""
    try:
        settings = get_bot_settings()
        if settings and "run_repetidas" in settings:
            return bool(settings.get("run_repetidas", 0))
        return False
    except Exception as e:
        print(f"⚠️  Error al obtener run_repetidas: {e}")
        return False

