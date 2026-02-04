"""
Cliente WebSocket para conectar bots a la API.

Este script integra el login existente con la conexión WebSocket.
"""

import socketio
import requests
import time
import sys
import threading
from datetime import datetime, timedelta
from app.database.database import save_user, get_logged_in_user, delete_logged_in_user

# Configuración
BASE_API_URL = "http://34.29.59.97/api/auth"
LOGIN_URL = f"{BASE_API_URL}/login"
VERIFY_TOKEN_URL = f"{BASE_API_URL}/verify-token"
WS_URL = "http://34.29.59.97"  # URL base para WebSocket

# Configuración del bot - se carga desde la base de datos
from app.database.database import get_bot_connection_config

def get_bot_config():
    """Obtiene la configuración del bot desde la base de datos"""
    config = get_bot_connection_config()
    return config.get("bot_name", "Mi Bot 1"), config.get("bot_type", "logueador")

# Crear cliente SocketIO
sio = socketio.Client()

# Variable global para controlar el bot
bot_running = False
bot_thread = None


def login(username, password):
    """Función de login existente"""
    payload = {"username": username, "password": password}

    try:
        response = requests.post(LOGIN_URL, json=payload)

        try:
            response_data = response.json()
        except ValueError:
            return {"error": "Error al procesar la respuesta del servidor"}

        if response.status_code != 200:
            return response_data 

        if "access_token" in response_data:
            user_data = {
                "id": response_data.get("id"),
                "name": response_data.get("name"),
                "lastname": response_data.get("lastname"),
                "access_token": response_data.get("access_token"),
            }
            save_user(user_data)
            return response_data  

        return {"error": "Respuesta inesperada del servidor"}

    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return {"error": "Error de conexión con el servidor"}


def verify_token():
    """Función de verificación de token existente"""
    user = get_logged_in_user()

    if not user:
        return {"is_valid": False}  

    access_token = user.get("access_token")
    user_id = user.get("id")

    if not access_token:
        return {"is_valid": False}

    payload = {"access_token": access_token}
    url = f"{VERIFY_TOKEN_URL}/{user_id}"

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            return response_data  
        else:
            return {"is_valid": False}

    except requests.RequestException as e:
        print(f"Error de conexión al verificar el token: {e}")
        return {"is_valid": False}


def logout():
    """Función para cerrar sesión: detiene el bot, desconecta WebSocket y elimina usuario local
    
    Returns:
        bool: True si había un usuario logueado y se cerró sesión correctamente, False si no había usuario
    """
    global bot_running
    
    # Verificar si hay un usuario logueado antes de proceder
    user = get_logged_in_user()
    if not user:
        print("⚠️  No hay usuario logueado para cerrar sesión")
        return False
    
    # Detener el bot si está corriendo
    if bot_running:
        bot_running = False
        print("🛑 Bot detenido durante logout")
    
    # Desconectar WebSocket si está conectado (enviando 'offline' antes)
    if sio.connected:
        try:
            sio.emit('status_update', {'status': 'offline'})
            time.sleep(0.3)  # Dar tiempo para que se envíe el mensaje
            sio.disconnect()
            print("🔌 WebSocket desconectado")
        except Exception as e:
            print(f"⚠️  Error al desconectar WebSocket: {e}")
    
    # Eliminar usuario de la base de datos local
    delete_logged_in_user()
    print("✅ Sesión cerrada correctamente")
    return True


# ========== HANDLERS DE WEBSOCKET ==========

@sio.event
def connect():
    """Se ejecuta cuando el bot se conecta exitosamente"""
    bot_name, _ = get_bot_config()
    print(f"✅ Bot '{bot_name}' conectado al servidor WebSocket")
    print(f"   Socket ID: {sio.sid}")
    # Notificar al servidor el estado actual (stopped si no está corriendo, running si está corriendo)
    try:
        if bot_running:
            sio.emit('status_update', {'status': 'running'})
            print("   📤 Estado 'running' enviado al servidor")
        else:
            sio.emit('status_update', {'status': 'stopped'})
            print("   📤 Estado 'stopped' enviado al servidor")
    except Exception as e:
        print(f"   ⚠️  Error al enviar status_update: {e}")


def send_status_update_with_next_cycle(status, next_cycle_at=None):
    """Envía una actualización de estado al servidor, incluyendo la hora del próximo ciclo."""
    if sio.connected:
        payload = {'status': status}
        if next_cycle_at:
            # Asegurar que next_cycle_at esté en formato ISO con 'Z' para UTC
            if isinstance(next_cycle_at, str):
                next_cycle_iso = next_cycle_at
            else:
                from datetime import datetime
                if isinstance(next_cycle_at, datetime):
                    next_cycle_iso = next_cycle_at.isoformat() + 'Z'
                else:
                    next_cycle_iso = None
            
            if next_cycle_iso:
                payload['next_cycle_at'] = next_cycle_iso
                print(f"📤 Enviando status_update: status={status}, next_cycle_at={next_cycle_iso}")
            else:
                payload['next_cycle_at'] = None
                print(f"📤 Enviando status_update: status={status}, next_cycle_at=None (formato inválido)")
        else:
            payload['next_cycle_at'] = None
            print(f"📤 Enviando status_update: status={status}, next_cycle_at=None")
        
        try:
            sio.emit('status_update', payload)
            print(f"✅ status_update enviado correctamente al servidor")
        except Exception as e:
            print(f"❌ Error al enviar status_update: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️  No se pudo enviar status_update: WebSocket no conectado")


@sio.event
def disconnect():
    """Se ejecuta cuando el bot se desconecta del servidor"""
    global bot_running
    bot_running = False
    print("❌ Bot desconectado del servidor WebSocket")
    # Nota: El servidor ya maneja la actualización del estado a 'offline' cuando detecta la desconexión


@sio.event
def connected(data):
    """Recibe confirmación de conexión del servidor"""
    print(f"✅ Conexión confirmada por el servidor")
    print(f"   Datos recibidos: {data}")
    bot_id = data.get('bot_id')
    status = data.get('status', 'unknown')
    message = data.get('message', '')
    
    if bot_id:
        print(f"   🆔 Bot ID asignado: {bot_id}")
    if status:
        print(f"   📊 Estado: {status}")
    if message:
        print(f"   💬 Mensaje: {message}")


@sio.event
def command(data):
    """Recibe comandos del servidor (start, stop, restart, etc.)"""
    global bot_running, bot_thread
    
    cmd = data.get('command')
    bot_id = data.get('bot_id')
    print(f"📨 Comando recibido: {cmd} (bot_id: {bot_id})")
    
    if cmd == 'start':
        # Verificar el estado real del thread, no solo la variable bot_running
        from app.ultrabot.ultra_bot import bot_thread as global_bot_thread
        thread_is_alive = global_bot_thread is not None and global_bot_thread.is_alive()
        
        if not bot_running and not thread_is_alive:
            print("🚀 Iniciando bot...")
            bot_running = True
            sio.emit('status_update', {'status': 'running'})
            
            # Ejecutar la función del bot logueador
            try:
                from app.ultrabot.ultra_bot import execute_ultra_bot
                print("✅ Ejecutando UltraBot (logueador)...")
                bot_thread = threading.Thread(target=execute_ultra_bot, daemon=True)
                bot_thread.start()
            except Exception as e:
                print(f"❌ Error al iniciar bot: {e}")
                import traceback
                traceback.print_exc()
                bot_running = False
                sio.emit('status_update', {'status': 'error', 'error_message': str(e)})
        else:
            # El bot ya está corriendo, sincronizar el estado con el servidor
            if thread_is_alive:
                print("⚠️  El bot ya está corriendo (thread activo detectado)")
                print("🔄 Sincronizando estado: enviando 'running' al servidor para actualizar la UI")
                # Enviar estado 'running' para sincronizar la UI
                try:
                    send_status_update_with_next_cycle('running', None)
                except:
                    # Si falla, enviar un status_update simple
                    sio.emit('status_update', {'status': 'running'})
            elif bot_running:
                # bot_running es True pero el thread no está vivo, corregir el estado
                print("⚠️  Estado inconsistente: bot_running=True pero thread no está vivo. Corrigiendo...")
                bot_running = False
                sio.emit('status_update', {'status': 'stopped'})
            else:
                print("⚠️  El bot ya está corriendo (según bot_running)")
                # Aunque bot_running sea True, enviar estado para sincronizar
                sio.emit('status_update', {'status': 'running'})
            
    elif cmd == 'stop':
        print("🛑 Deteniendo bot...")
        bot_running = False
        # Detener el bot siempre, independientemente del estado
        try:
            from app.ultrabot.ultra_bot import stop_ultra_bot
            stop_ultra_bot()
            print("✅ Bot detenido correctamente")
        except Exception as e:
            print(f"⚠️  Error al detener bot: {e}")
            import traceback
            traceback.print_exc()
        # Asegurar que el estado sea 'stopped' en el servidor
        sio.emit('status_update', {'status': 'stopped'})
            
    elif cmd == 'restart':
        print("🔄 Reiniciando bot...")
        if bot_running:
            bot_running = False
            try:
                from app.ultrabot.ultra_bot import stop_ultra_bot
                stop_ultra_bot()
            except Exception as e:
                print(f"⚠️  Error al detener bot: {e}")
            time.sleep(1)
        bot_running = True
        sio.emit('status_update', {'status': 'running'})
        
        # Reiniciar la función del bot
        try:
            from app.ultrabot.ultra_bot import execute_ultra_bot
            print("✅ Reiniciando UltraBot (logueador)...")
            bot_thread = threading.Thread(target=execute_ultra_bot, daemon=True)
            bot_thread.start()
        except Exception as e:
            print(f"❌ Error al reiniciar bot: {e}")
            import traceback
            traceback.print_exc()
            bot_running = False
            sio.emit('status_update', {'status': 'error', 'error_message': str(e)})
    
    elif cmd == 'close_ultra':
        print("🪟 Cerrando ventana de Ultra...")
        try:
            from app.ultrabot.ultra_bot import click_coordinates
            result = click_coordinates(1339, 10)
            if result:
                print("✅ Comando de cerrar Ultra ejecutado")
                # Enviar confirmación al servidor
                if sio.connected:
                    sio.emit('action_completed', {
                        'action': 'close_ultra',
                        'success': True,
                        'message': 'Ventana de Ultra cerrada exitosamente'
                    })
            else:
                print("⚠️  Error al ejecutar clic en coordenadas")
                if sio.connected:
                    sio.emit('action_completed', {
                        'action': 'close_ultra',
                        'success': False,
                        'message': 'Error al cerrar la ventana de Ultra'
                    })
        except Exception as e:
            print(f"⚠️  Error al cerrar Ultra: {e}")
            import traceback
            traceback.print_exc()
            if sio.connected:
                sio.emit('action_completed', {
                    'action': 'close_ultra',
                    'success': False,
                    'message': f'Error al cerrar Ultra: {str(e)}'
                })
    
    elif cmd == 'delete_cache':
        print("🗑️ Eliminando cache de Ultra...")
        try:
            from app.ultrabot.utils_ultrabot import handle_delete_ultra_folder
            result = handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
            if result:
                print("✅ Cache de Ultra eliminado correctamente")
                # Enviar confirmación al servidor
                if sio.connected:
                    sio.emit('action_completed', {
                        'action': 'delete_cache',
                        'success': True,
                        'message': 'Cache de Ultra eliminada exitosamente'
                    })
            else:
                print("⚠️  No se pudo eliminar la cache de Ultra completamente")
                if sio.connected:
                    sio.emit('action_completed', {
                        'action': 'delete_cache',
                        'success': False,
                        'message': 'No se pudo eliminar la cache de Ultra completamente'
                    })
        except Exception as e:
            print(f"⚠️  Error al eliminar cache: {e}")
            import traceback
            traceback.print_exc()
            if sio.connected:
                sio.emit('action_completed', {
                    'action': 'delete_cache',
                    'success': False,
                    'message': f'Error al eliminar cache: {str(e)}'
                })


def connect_bot():
    """Conecta el bot al servidor vía WebSocket"""
    user = get_logged_in_user()
    
    if not user:
        print("❌ No hay usuario logueado. Ejecuta login() primero.")
        return False
    
    access_token = user.get("access_token")
    if not access_token:
        print("❌ No hay access_token disponible.")
        return False
    
    # Verificar que el token sea válido
    print("🔍 Verificando token...")
    verify_result = verify_token()
    if not verify_result.get("is_valid", False):
        print("❌ Token inválido o expirado. Haz login nuevamente.")
        return False
    print("✅ Token válido")
    
    # Si ya está conectado, desconectar primero (enviando 'offline' antes)
    if sio.connected:
        print("⚠️  Ya hay una conexión activa. Desconectando...")
        try:
            sio.emit('status_update', {'status': 'offline'})
            time.sleep(0.3)  # Dar tiempo para que se envíe el mensaje
        except Exception as e:
            print(f"⚠️  Error al enviar estado offline: {e}")
        try:
            sio.disconnect()
            time.sleep(0.5)  # Esperar un momento antes de reconectar
        except Exception as e:
            print(f"⚠️  Error al desconectar: {e}")
    
    try:
        # Obtener configuración del bot desde la base de datos
        bot_name, bot_type = get_bot_config()
        
        # Conectar al servidor con autenticación
        print(f"🔌 Conectando bot '{bot_name}' al servidor {WS_URL}...")
        print(f"   Tipo de bot: {bot_type}")
        
        sio.connect(
            WS_URL,
            auth={
                'access_token': access_token,
                'bot_name': bot_name,
                'bot_type': bot_type
            },
            wait_timeout=10,
            transports=['websocket', 'polling']  # Intentar ambos métodos
        )
        
        print("✅ Conexión WebSocket establecida")
        return True
        
    except socketio.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Verifica que:")
        print("  1. El servidor esté corriendo en " + WS_URL)
        print("  2. La URL sea correcta")
        print("  3. El servidor tenga WebSockets habilitados")
        print("  4. No haya problemas de firewall o red")
        return False
    except socketio.exceptions.TimeoutError as e:
        print(f"❌ Timeout al conectar: {e}")
        print("   El servidor no respondió a tiempo")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al conectar: {e}")
        import traceback
        traceback.print_exc()
        return False
