"""
Flujos de ejecución del Ultra Bot: modo Sqlite (sync a Partitions) y modo UI (cookie por pestaña).
"""
from __future__ import annotations

import time
from tkinter import messagebox

import app.ultrabot.ultra_bot as ub


def run_ultra_bot_sqlite_thread(thread) -> None:
    """Logueo con Sqlite: lote de cuentas → Partitions → sync Cookies → activación."""
    self = thread
    print("\n" + "="*60)
    print("🚀 INICIANDO ULTRA BOT")
    print("="*60)
    print("⏳ Esperando 3 segundos antes de comenzar...")
    if not self.safe_sleep(3):
        print("🛑 Bot detenido antes de iniciar")
        return
    
    # Verificar ANTES de buscar el logo
    if not self.running:
        print("🛑 Bot detenido antes de buscar logo")
        return
    
    print("🖱️ Buscando logo de Ultra...")
    # Reducir intentos para que responda más rápido si se detiene
    if not ub.click_ultra_logo(max_attempts=3, delay_between_attempts=1):
        # Verificar si fue porque se detuvo el bot
        if not self.running:
            print("🛑 Bot detenido durante búsqueda del logo")
            return
        messagebox.showerror("Error", "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.")
        print("❌ No se pudo hacer clic en el logo de Ultra")
        return
    print("✅ Logo de Ultra encontrado y clickeado")
    
    # Verificar inmediatamente después del clic
    if not self.running:
        print("🛑 Bot detenido después de hacer clic en logo")
        return
    
    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
    if not self.safe_sleep(40):
        print("🛑 Bot detenido durante espera inicial")
        return
    print("✅ Espera inicial completada")
    # ub.click_europa_boton()
    # time.sleep(1)
    # ub.click_europa_boton2()

    # ub.login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
    print("🔐 Iniciando proceso de login en Ultra...")
    if not ub.login_with_ultra_credentials():
        print("❌ Login fallido")
        return  # El mensaje de error ya fue mostrado por ub.login_with_ultra_credentials()
    
    if not self.running:
        print("🛑 Bot detenido después de login")
        return
    print("✅ Login exitoso en Ultra")
    
    print("⏳ Esperando 15 segundos después del login...")
    if not self.safe_sleep(15):
        print("🛑 Bot detenido durante espera post-login")
        return
    print("✅ Espera post-login completada")
    
    # Verificar errores de Ultra y recuperar si es necesario
    print("\n🔍 Verificando que Ultra haya cargado correctamente...")
    if not ub.check_ultra_error_and_recover(max_attempts=5):
        print("❌ Ultra no cargó correctamente después de múltiples intentos")
        messagebox.showerror("Error de Ultra", "Ultra no está cargando correctamente después del login. El proceso se detendrá.")
        return
    
    if not self.running:
        print("🛑 Bot detenido después de verificación de errores de Ultra")
        return
    
    print("✅ Ultra cargó correctamente, continuando con el ciclo normal...")

    print("\n📋 Obteniendo configuración del bot...")
    config = ub.get_bot_settings()

    if config:
        MAX_ITERATIONS = config["iterations"]
        TIEMPO_ESPERA = config["interval_seconds"]
    else:
        MAX_ITERATIONS = 16
        TIEMPO_ESPERA = 7200

    # Verificar si se deben usar cuentas locales
    use_local = ub.get_use_local_accounts()
    
    print(f"⚙️ Configuración cargada:")
    print(f"   - Iteraciones: {MAX_ITERATIONS}")
    print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
    if use_local:
        print("📦 Modo: Usando cuentas de la base de datos local")
    else:
        print("🌐 Modo: Obteniendo cuentas del servidor")
    
    iteration_count = 0
    # Tras cargar cookies en lote (sync a disco), se rellena y se iguala iteration_count
    # para disparar el mismo bloque que antes (una iteración por cuenta hasta MAX_ITERATIONS).
    pending_activation_batch = None  # int o None: cuentas listas para activar tabs
    print("\n🔄 Iniciando bucle principal de procesamiento...")

    
    # Calcular y enviar la próxima hora del ciclo al servidor
    try:
        from datetime import datetime, timedelta
        from app.auth.auth import send_status_update_with_next_cycle
        
        # Calcular la próxima hora del ciclo: ahora + TIEMPO_ESPERA segundos
        next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
        print(f"📅 Calculando próximo ciclo...")
        print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
        print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Enviar al servidor usando la función auxiliar
        send_status_update_with_next_cycle('running', next_cycle)
        print(f"✅ Próximo ciclo enviado al servidor correctamente")
    except Exception as e:
        print(f"⚠️  Error al calcular/enviar próxima hora del ciclo: {e}")
        import traceback
        traceback.print_exc()

    # Cargar cuentas según la preferencia
    if use_local:
        # Usar cuentas locales
        local_count = ub.get_cookie_count()
        if local_count == 0:
            print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
            use_local = False
        else:
            print(f"📦 Usando {local_count} cuentas de la base de datos local")
            if local_count < MAX_ITERATIONS:
                print(f"⚠️ Solo hay {local_count} cuentas locales, pero se necesitan {MAX_ITERATIONS}")
            # Asegurar que ub.last_cookie_id esté en 1 cuando se usan cuentas locales
            ub.last_cookie_id = 1
            print(f"🔄 ub.last_cookie_id inicializado en {ub.last_cookie_id} para modo local")
    
    if not use_local:
        # Obtener cuentas del servidor
        print("🗑️ Limpiando base de datos...")
        ub.clear_database()
        print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
        accounts = ub.fetch_accounts_from_server(MAX_ITERATIONS)
        
        if not accounts:
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        
        print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
        ub.save_cookies_to_db(accounts)
        
        # Verificar que las cookies se guardaron correctamente
        saved_count = ub.get_cookie_count()
        if saved_count == 0:
            messagebox.showerror("Error", f"No se pudieron guardar las cuentas en la base de datos. Se obtuvieron {len(accounts)} cuentas pero no se guardaron.")
            return
        print(f"✅ Se guardaron {saved_count} cuentas en la base de datos")
        
        # Asegurar que ub.last_cookie_id esté en 1 después de limpiar la base de datos
        ub.last_cookie_id = 1
        print(f"🔄 ub.last_cookie_id inicializado en {ub.last_cookie_id}")

    while self.running:
        # Verificar periódicamente si se debe detener
        if not self.running:
            print("🛑 Bot detenido - saliendo del bucle principal")
            break
        
        if iteration_count >= MAX_ITERATIONS or (
            pending_activation_batch is not None
            and iteration_count >= pending_activation_batch
        ):
            if not self.running:
                print("🛑 Bot detenido antes de procesar tabs")
                break

            work_batch = (
                pending_activation_batch
                if pending_activation_batch is not None
                else MAX_ITERATIONS
            )
            pending_activation_batch = None

            print(
                f"\n📊 Carga de cookies completada ({work_batch} cuenta(s)). "
                f"Iniciando proceso de tabs (activación)..."
            )

            # Antes de "Start all tabs": solo linkedincargabien.PNG debe estar visible.
            # Si no: cerrar Ultra, reabrir, esperar 30 s, verificar login/carga y reintentar (máx. 5).
            LINKEDIN_PRE_START_MAX_RETRIES = 5
            POLL_INTERVAL = 0.5
            POLL_SECONDS_PER_ATTEMPT = 20.0  # ventana de búsqueda tras Europa antes de reiniciar
            activation_ready = False
            for load_attempt in range(LINKEDIN_PRE_START_MAX_RETRIES):
                if not self.running:
                    break
                if load_attempt > 0:
                    print(
                        f"🔄 Reintentando detección de linkedincargabien "
                        f"({load_attempt + 1}/{LINKEDIN_PRE_START_MAX_RETRIES})..."
                    )

                ub.click_europa_boton()
                if not self.safe_sleep(1):
                    break
                ub.click_europa_boton2()
                if not self.safe_sleep(2):
                    break

                print(
                    f"🔍 Buscando {ub.LINKEDIN_CARGA_BIEN_IMAGE} (hasta {POLL_SECONDS_PER_ATTEMPT:.0f}s)..."
                )
                _polls = max(1, int(POLL_SECONDS_PER_ATTEMPT / POLL_INTERVAL))
                seen_linkedin = False
                for _ in range(_polls):
                    if not self.running:
                        break
                    if ub.linkedin_carga_bien_visible(confidence=0.65):
                        print(
                            "✅ linkedincargabien detectado. Continuando con Start all tabs..."
                        )
                        seen_linkedin = True
                        break
                    if not self.safe_sleep(POLL_INTERVAL):
                        break

                if seen_linkedin:
                    activation_ready = True
                    break

                print(
                    "⚠️ No se detectó linkedincargabien; cerrando Ultra, reabriendo y "
                    f"esperando 30 s antes de volver a verificar..."
                )
                if load_attempt >= LINKEDIN_PRE_START_MAX_RETRIES - 1:
                    break

                # Cerrar ventana primero; luego esperar y recién ahí terminar procesos (evita locks).
                ub.click_coordinates(1339, 10)
                print("⏳ Esperando 5 s tras cerrar la ventana antes de terminar procesos de Ultra...")
                if not self.safe_sleep(5):
                    break
                try:
                    ub.kill_ultra_processes(show_confirmation=False)
                except Exception as e:
                    print(f"⚠️ Error al terminar procesos de Ultra: {e}")
                    import traceback

                    traceback.print_exc()

                print("🔄 Abriendo Ultra de nuevo (logo)...")
                if not ub.click_ultra_logo(max_attempts=3, delay_between_attempts=1):
                    print("❌ No se pudo hacer clic en el logo de Ultra")
                    break

                print("⏳ Esperando 30 s para que Ultra estabilice tras reabrir...")
                if not self.safe_sleep(30):
                    break

                if not ub.check_ultra_error_and_recover(max_attempts=5):
                    print(
                        "⚠️ Ultra no pasó la verificación tras el reinicio; "
                        "se intentará de nuevo..."
                    )

            if not activation_ready:
                if self.running:
                    messagebox.showerror(
                        "LinkedIn / Ultra",
                        "No se pudo detectar linkedincargabien.PNG después de varios intentos.\n\n"
                        "No se ejecutará Start all tabs.",
                    )
                break

            ub.click_start_all_tabs()
            if not self.safe_sleep(2):
                break
            ub.click_europa_boton()
            if not self.safe_sleep(1):
                break
            ub.click_europa_boton2()

            if not ub.click_acept_actionTabs():
                if not self.safe_sleep(1):
                    break
                ub.click_acept_actionTabs()

            tiempo_por_parte = TIEMPO_ESPERA // 4
            print(f"⏳ Esperando {tiempo_por_parte}s por parte (total: {TIEMPO_ESPERA}s)")
            if not self.safe_sleep(tiempo_por_parte):
                print("🛑 Bot detenido durante espera de tabs")
                break
            
            # Constantes para el manejo de errores de LinkedIn
            ERROR_LINKEDIN_PATH = "app/ultrabot/images/accionesVentana/ErrorLinkedin.PNG"
            MAX_INTENTOS_ERROR = 10
            COORD_ERROR_CLOSE = (915, 438)
            
            for parte in range(3):
                if not self.running:
                    print("🛑 Bot detenido durante procesamiento de partes")
                    break
                    
                print(f"📍 Procesando parte {parte + 1}/3...")
                # Primero cerrar la ventana de Ultra
                ub.click_coordinates(1339, 10)
                if not self.safe_sleep(5):
                    break
                
                # Luego eliminar los procesos de Ultra después de cerrar la ventana
                # Envolver kill_ultra_processes en try-except para evitar que cierre el bot
                try:
                    ub.kill_ultra_processes(show_confirmation=False)
                except Exception as e:
                    print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                    import traceback
                    traceback.print_exc()

                for intento_error in range(MAX_INTENTOS_ERROR):
                    if not self.running:
                        break
                    ub.click_ultra_logo()
                    if not self.safe_sleep(3):
                        break
                    
                    if not ub.find_image(ERROR_LINKEDIN_PATH, confidence=0.7):
                        break
                    
                    ub.click_coordinates(*COORD_ERROR_CLOSE)
                    if not self.safe_sleep(1):
                        break
                
                if not self.running:
                    break
                
                if not self.safe_sleep(15):
                    break
                time.sleep(90)
                ub.click_start_all_tabs() 
                if not self.safe_sleep(2):
                    break
                if not ub.click_acept_actionTabs():
                    if not self.safe_sleep(1):
                        break
                    ub.click_acept_actionTabs()                
                
                if not self.safe_sleep(tiempo_por_parte):
                    print("🛑 Bot detenido durante espera de parte")
                    break


            if not self.running:
                break
                
            ub.click_europa_boton()
            if not self.safe_sleep(1):
                break
            ub.click_europa_boton2()
            

            print("⏹️ Deteniendo todas las tabs...")
            ub.click_stop_all_tabs()
            if not self.safe_sleep(2):
                break

            if not ub.click_acept_stop_actionTabs():
                if not self.safe_sleep(1):
                    break
                ub.click_acept_stop_actionTabs()
                if not self.safe_sleep(2):
                    break

            print(f"🗑️ Cerrando {work_batch} ventanas...")
            if not self.safe_sleep(2):
                break
            for _ in range(work_batch):
                if not self.running:
                    break
                ub.click_close_window()
                if not self.safe_sleep(0.5):
                    break

            if not self.running:
                break
                
            ub.click_coordinates(1339, 10)
            if not self.safe_sleep(5):
                break
            
            print("🔪 Eliminando procesos de Ultra...")
            # Envolver kill_ultra_processes en try-except para evitar que cierre el bot
            try:
                ub.kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                import traceback
                traceback.print_exc()
            
            print("🗑️ Eliminando cache de Ultra...")
            cache_deleted = False
            max_cache_attempts = 3
            
            for cache_attempt in range(max_cache_attempts):
                cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                
                if cache_deleted:
                    print("✅ Cache eliminada")
                    break
                else:
                    if cache_attempt < max_cache_attempts - 1:
                        if not self.safe_sleep(5):
                            break
                        try:
                            ub.kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
            
            if not cache_deleted:
                messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                break
            
            print("🔄 Reiniciando login...")
            max_restart_attempts = 3
            login_successful = False
            
            for restart_attempt in range(max_restart_attempts):
                print(f"🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                if ub.click_ultra_logo():
                    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                    time.sleep(40)
                    if ub.wait_for_login_interface(max_attempts=3, wait_time=15):
                        # ub.login_with_ultra_credentials() ya muestra el mensaje de error si falla después de 5 intentos
                        if ub.login_with_ultra_credentials():
                            time.sleep(2)
                            login_successful = True
                            break
                        else:
                            login_successful = False
                        break
                    else:
                        if restart_attempt < max_restart_attempts - 1:
                            ub.click_coordinates(1339, 10)
                            time.sleep(5)
                            try:
                                ub.kill_ultra_processes(show_confirmation=False)
                            except Exception as e:
                                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                            cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                else:
                    if restart_attempt < max_restart_attempts - 1:
                        ub.click_coordinates(1339, 10)
                        time.sleep(5)
                        try:
                            ub.kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                        cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
            
            if not login_successful:
                messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                break
            
            print("🔄 Reiniciando ciclo...")
            
            # Calcular y enviar la nueva próxima hora del ciclo al servidor
            try:
                from datetime import datetime, timedelta
                from app.auth.auth import send_status_update_with_next_cycle
                
                # Calcular la próxima hora del ciclo: ahora + TIEMPO_ESPERA segundos
                next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
                print(f"📅 Recalculando próximo ciclo después de reinicio...")
                print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
                print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Enviar al servidor usando la función auxiliar
                send_status_update_with_next_cycle('running', next_cycle)
                print(f"✅ Próximo ciclo recalculado y enviado al servidor correctamente")
            except Exception as e:
                print(f"⚠️  Error al recalcular/enviar próxima hora del ciclo: {e}")
                import traceback
                traceback.print_exc()
            
            # Verificar nuevamente si se deben usar cuentas locales
            use_local = ub.get_use_local_accounts()
            
            if use_local:
                local_count = ub.get_cookie_count()
                if local_count == 0:
                    print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
                    use_local = False
                else:
                    print(f"📦 Usando {local_count} cuentas de la base de datos local")
            
            if not use_local:
                ub.clear_database()
                print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
                accounts = ub.fetch_accounts_from_server(MAX_ITERATIONS)
                
                if not accounts:
                    messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                    break
                
                print(f"✅ Se obtuvieron {len(accounts)} nuevas cuentas del servidor")
                ub.save_cookies_to_db(accounts)
            
            iteration_count = 0  # 🔄 Resetear contador para que vuelva a iniciar
            ub.last_cookie_id = 1  # 🔄 Resetear el ID de cookie
            continue  # ⏭️ Reinicia el bucle sin procesar más cookies

        iteration_count += 1

        if not self.running:
            print("🛑 Bot detenido durante el bucle principal")
            break

        # Fase 1 (iteration_count == 1 tras el incremento): configuración → pestañas →
        # cerrar Ultra → kill → sincronizar Cookies en disco. Luego iteration_count pasa
        # a batch_size y se dispara el bloque de activación de tabs (arriba).
        if iteration_count != 1:
            print(
                "⚠️ iteration_count inesperado en fase de carga de cookies; "
                f"esperado 1, recibido {iteration_count}. Deteniendo."
            )
            break

        # Todas las filas en BD (servidor o local): una pestaña/partición por cookie.
        batch_size = ub.get_cookie_count()
        if batch_size == 0:
            messagebox.showerror(
                "Error",
                "No hay cuentas en la base de datos para sincronizar con Partitions.",
            )
            break
        if batch_size != MAX_ITERATIONS:
            print(
                f"ℹ️ Cuentas en BD ({batch_size}) ≠ iteraciones configuradas ({MAX_ITERATIONS}). "
                f"Se abrirán {batch_size} pestañas y se validará contra {batch_size} particiones."
            )

        print(
            f"🔄 Iteración {iteration_count}/{MAX_ITERATIONS}: "
            f"lote de {batch_size} cuenta(s) en BD — fila i (ORDER BY id) → partición i (orden creación)."
        )

        ub.click_ultra_internal_config()

        time.sleep(2)
        for tab_i in range(batch_size):
            if not self.running:
                break
            ub.click_add_account()
            if tab_i < batch_size - 1:
                time.sleep(2)

        if not self.running:
            break
        time.sleep(5)
        if not self.safe_sleep(2):
            break
        ub.click_coordinates(1339, 10)

        if not self.safe_sleep(2):
            break

        # Dar tiempo a que suelte handles; Ultra a veces sigue usando Cookies tras cerrar la ventana.
        print("⏳ Esperando antes de forzar cierre de procesos de Ultra...")
        if not self.safe_sleep(4):
            break

        try:
            ub.kill_ultra_processes(show_confirmation=False)
        except Exception as e:
            print(f"⚠️ Error al terminar procesos de Ultra (continuando): {e}")
            import traceback
            traceback.print_exc()

        print("⏳ Esperando a que el sistema libere los archivos Cookies...")
        if not self.safe_sleep(5):
            break

        # Ultra a veces tarda en crear carpetas bajo Partitions tras cerrar; reintentar el conteo.
        print(
            "⏳ Esperando a que existan carpetas en Partitions (puede tardar unos segundos)..."
        )
        if not self.safe_sleep(5):
            break

        n_db = ub.get_cookie_count()
        PARTITION_POLL_INTERVAL = 3.0
        PARTITION_POLL_MAX_ROUNDS = 20  # hasta ~60 s extra además de la espera previa
        n_part = 0
        for poll_round in range(PARTITION_POLL_MAX_ROUNDS):
            if not self.running:
                break
            n_part = ub.count_partition_folders()
            print(
                f"📂 Partitions: {n_part} carpetas | BD: {n_db} filas | "
                f"lote esperado: {batch_size} (comprobación {poll_round + 1}/{PARTITION_POLL_MAX_ROUNDS})"
            )
            if n_part >= batch_size:
                print("✅ Número de particiones ≥ lote esperado.")
                break
            if poll_round < PARTITION_POLL_MAX_ROUNDS - 1:
                if not self.safe_sleep(PARTITION_POLL_INTERVAL):
                    break

        # Flexible: sincronizar tantas parejas como permita min(BD, Partitions); no abortar si falta 1 carpeta.
        if n_db != batch_size:
            print(
                f"⚠️ Filas en BD ({n_db}) ≠ lote inicial ({batch_size}); se usará min(BD, particiones)."
            )

        if n_part == 0:
            messagebox.showerror(
                "Error de Partitions",
                "No hay ninguna carpeta bajo Partitions después de esperar.\n\n"
                "Ultra no creó particiones o la ruta no es accesible. No se puede sincronizar.",
            )
            break

        n_sync = min(n_db, n_part)
        if n_part < batch_size:
            print(
                "⚠️ Particiones incompletas: Ultra aún no generó todas las carpetas.\n"
                f"   • Carpetas detectadas: {n_part}\n"
                f"   • Cuentas en lote: {batch_size}\n"
                f"   • Se sincronizan: {n_sync} parejas (BD ↔ partición)\n"
                "   El resto queda en BD sin escribir en disco en esta pasada."
            )
        elif n_part > batch_size:
            print(
                f"ℹ️ Hay más carpetas en Partitions ({n_part}) que cuentas en el lote ({batch_size}); "
                f"la sincronización usará las primeras {batch_size} parejas por orden (BD / creación)."
            )

        if n_sync == 0:
            messagebox.showerror(
                "Error",
                "No hay parejas BD–partición para sincronizar (n_sync=0).",
            )
            break

        print("\n📂 Sincronizando archivos Cookies en cada carpeta Network desde la base de datos...")
        sync_code = ub.sync_ultra_partitions_network_cookies()
        if sync_code < 0:
            print("❌ No se pudo completar la sincronización de cookies en disco.")
            break

        print(
            "\n✅ Cookies escritas en disco. Pasando a activación de cuentas (proceso de tabs)..."
        )
        ub.click_ultra_logo()
        if not self.safe_sleep(3):
            break
        time.sleep(600)
        # Activación con el número real de cuentas sincronizadas a particiones (puede ser < batch_size).
        pending_activation_batch = n_sync
        iteration_count = n_sync
        continue


def run_ultra_bot_ui_thread(thread) -> None:
    """Logueo con UI: una cuenta por iteración (pestaña + cookie en la interfaz)."""
    self = thread
    print("\n" + "="*60)
    print("🚀 INICIANDO ULTRA BOT")
    print("="*60)
    print("⏳ Esperando 3 segundos antes de comenzar...")
    if not self.safe_sleep(3):
        print("🛑 Bot detenido antes de iniciar")
        return
    if not self.running:
        print("🛑 Bot detenido antes de buscar logo")
        return
    print("🖱️ Buscando logo de Ultra...")
    if not ub.click_ultra_logo(max_attempts=3, delay_between_attempts=1):
        if not self.running:
            print("🛑 Bot detenido durante búsqueda del logo")
            return
        messagebox.showerror("Error", "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.")
        print("❌ No se pudo hacer clic en el logo de Ultra")
        return
    print("✅ Logo de Ultra encontrado y clickeado")
    if not self.running:
        print("🛑 Bot detenido después de hacer clic en logo")
        return
    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
    if not self.safe_sleep(40):
        print("🛑 Bot detenido durante espera inicial")
        return
    print("✅ Espera inicial completada")
    print("🔐 Iniciando proceso de login en Ultra...")
    if not ub.login_with_ultra_credentials():
        print("❌ Login fallido")
        return
    if not self.running:
        print("🛑 Bot detenido después de login")
        return
    print("✅ Login exitoso en Ultra")
    print("⏳ Esperando 15 segundos después del login...")
    if not self.safe_sleep(15):
        print("🛑 Bot detenido durante espera post-login")
        return
    print("✅ Espera post-login completada")
    print("\n🔍 Verificando que Ultra haya cargado correctamente...")
    if not ub.check_ultra_error_and_recover(max_attempts=5):
        print("❌ Ultra no cargó correctamente después de múltiples intentos")
        messagebox.showerror("Error de Ultra", "Ultra no está cargando correctamente después del login. El proceso se detendrá.")
        return
    if not self.running:
        print("🛑 Bot detenido después de verificación de errores de Ultra")
        return
    print("✅ Ultra cargó correctamente, continuando con el ciclo normal...")
    print("\n📋 Obteniendo configuración del bot...")
    config = ub.get_bot_settings()
    if config:
        MAX_ITERATIONS = config["iterations"]
        TIEMPO_ESPERA = config["interval_seconds"]
    else:
        MAX_ITERATIONS = 16
        TIEMPO_ESPERA = 7200
    use_local = ub.get_use_local_accounts()
    print(f"⚙️ Configuración cargada:")
    print(f"   - Iteraciones: {MAX_ITERATIONS}")
    print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
    if use_local:
        print("📦 Modo: Usando cuentas de la base de datos local")
    else:
        print("🌐 Modo: Obteniendo cuentas del servidor")
    iteration_count = 0
    print("\n🔄 Iniciando bucle principal de procesamiento...")
    try:
        from datetime import datetime, timedelta
        from app.auth.auth import send_status_update_with_next_cycle
        next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
        print(f"📅 Calculando próximo ciclo...")
        print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
        print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
        send_status_update_with_next_cycle('running', next_cycle)
        print(f"✅ Próximo ciclo enviado al servidor correctamente")
    except Exception as e:
        print(f"⚠️  Error al calcular/enviar próxima hora del ciclo: {e}")
        import traceback
        traceback.print_exc()
    if use_local:
        local_count = ub.get_cookie_count()
        if local_count == 0:
            print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
            use_local = False
        else:
            print(f"📦 Usando {local_count} cuentas de la base de datos local")
            if local_count < MAX_ITERATIONS:
                print(f"⚠️ Solo hay {local_count} cuentas locales, pero se necesitan {MAX_ITERATIONS}")
            ub.last_cookie_id = 1
            print(f"🔄 last_cookie_id inicializado en {ub.last_cookie_id} para modo local")
    if not use_local:
        print("🗑️ Limpiando base de datos...")
        ub.clear_database()
        print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
        accounts = ub.fetch_accounts_from_server(MAX_ITERATIONS)
        if not accounts:
            messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
            return
        print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
        ub.save_cookies_to_db(accounts)
        saved_count = ub.get_cookie_count()
        if saved_count == 0:
            messagebox.showerror("Error", f"No se pudieron guardar las cuentas en la base de datos. Se obtuvieron {len(accounts)} cuentas pero no se guardaron.")
            return
        print(f"✅ Se guardaron {saved_count} cuentas en la base de datos")
        ub.last_cookie_id = 1
        print(f"🔄 last_cookie_id inicializado en {ub.last_cookie_id}")

    while self.running:
        if not self.running:
            print("🛑 Bot detenido - saliendo del bucle principal")
            break
        if iteration_count >= MAX_ITERATIONS:
            if not self.running:
                print("🛑 Bot detenido antes de procesar tabs")
                break
            print(f"\n📊 Completadas {MAX_ITERATIONS} iteraciones. Iniciando proceso de tabs...")
            ub.click_europa_boton()
            if not self.safe_sleep(1):
                break
            ub.click_europa_boton2()
            if not self.safe_sleep(2):
                break
            ub.click_start_all_tabs()
            if not self.safe_sleep(2):
                break
            ub.click_europa_boton()
            if not self.safe_sleep(1):
                break
            ub.click_europa_boton2()
            if not ub.click_acept_actionTabs():
                if not self.safe_sleep(1):
                    break
                ub.click_acept_actionTabs()
            tiempo_por_parte = TIEMPO_ESPERA // 4
            print(f"⏳ Esperando {tiempo_por_parte}s por parte (total: {TIEMPO_ESPERA}s)")
            if not self.safe_sleep(tiempo_por_parte):
                print("🛑 Bot detenido durante espera de tabs")
                break
            ERROR_LINKEDIN_PATH = "app/ultrabot/images/accionesVentana/ErrorLinkedin.PNG"
            MAX_INTENTOS_ERROR = 10
            COORD_ERROR_CLOSE = (915, 438)
            for parte in range(3):
                if not self.running:
                    print("🛑 Bot detenido durante procesamiento de partes")
                    break
                print(f"📍 Procesando parte {parte + 1}/3...")
                ub.click_coordinates(1339, 10)
                if not self.safe_sleep(5):
                    break
                try:
                    ub.kill_ultra_processes(show_confirmation=False)
                except Exception as e:
                    print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                    import traceback
                    traceback.print_exc()
                for intento_error in range(MAX_INTENTOS_ERROR):
                    if not self.running:
                        break
                    ub.click_ultra_logo()
                    if not self.safe_sleep(3):
                        break
                    if not ub.find_image(ERROR_LINKEDIN_PATH, confidence=0.7):
                        break
                    ub.click_coordinates(*COORD_ERROR_CLOSE)
                    if not self.safe_sleep(1):
                        break
                if not self.running:
                    break
                if not self.safe_sleep(15):
                    break
                ub.click_start_all_tabs()
                if not self.safe_sleep(2):
                    break
                if not ub.click_acept_actionTabs():
                    if not self.safe_sleep(1):
                        break
                    ub.click_acept_actionTabs()
                if not self.safe_sleep(tiempo_por_parte):
                    print("🛑 Bot detenido durante espera de parte")
                    break
            if not self.running:
                break
            ub.click_europa_boton()
            if not self.safe_sleep(1):
                break
            ub.click_europa_boton2()
            print("⏹️ Deteniendo todas las tabs...")
            ub.click_stop_all_tabs()
            if not self.safe_sleep(2):
                break
            if not ub.click_acept_stop_actionTabs():
                if not self.safe_sleep(1):
                    break
                ub.click_acept_stop_actionTabs()
                if not self.safe_sleep(2):
                    break
            print(f"🗑️ Cerrando {MAX_ITERATIONS} ventanas...")
            if not self.safe_sleep(2):
                break
            for _ in range(MAX_ITERATIONS):
                if not self.running:
                    break
                ub.click_close_window()
                if not self.safe_sleep(0.5):
                    break
            if not self.running:
                break
            ub.click_coordinates(1339, 10)
            if not self.safe_sleep(5):
                break
            print("🔪 Eliminando procesos de Ultra...")
            try:
                ub.kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                import traceback
                traceback.print_exc()
            print("🗑️ Eliminando cache de Ultra...")
            cache_deleted = False
            max_cache_attempts = 3
            for cache_attempt in range(max_cache_attempts):
                cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=45)
                if cache_deleted:
                    print("✅ Cache eliminada")
                    break
                else:
                    if cache_attempt < max_cache_attempts - 1:
                        if not self.safe_sleep(5):
                            break
                        try:
                            ub.kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
            if not cache_deleted:
                messagebox.showerror("Error", "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.")
                break
            print("🔄 Reiniciando login...")
            max_restart_attempts = 3
            login_successful = False
            for restart_attempt in range(max_restart_attempts):
                print(f"🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
                if ub.click_ultra_logo():
                    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
                    time.sleep(40)
                    if ub.wait_for_login_interface(max_attempts=3, wait_time=15):
                        if ub.login_with_ultra_credentials():
                            time.sleep(2)
                            login_successful = True
                            break
                        else:
                            login_successful = False
                        break
                    else:
                        if restart_attempt < max_restart_attempts - 1:
                            ub.click_coordinates(1339, 10)
                            time.sleep(5)
                            try:
                                ub.kill_ultra_processes(show_confirmation=False)
                            except Exception as e:
                                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                            cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
                else:
                    if restart_attempt < max_restart_attempts - 1:
                        ub.click_coordinates(1339, 10)
                        time.sleep(5)
                        try:
                            ub.kill_ultra_processes(show_confirmation=False)
                        except Exception as e:
                            print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                        cache_deleted = ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
            if not login_successful:
                messagebox.showerror("Error", "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.")
                break
            print("🔄 Reiniciando ciclo...")
            try:
                from datetime import datetime, timedelta
                from app.auth.auth import send_status_update_with_next_cycle
                next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
                print(f"📅 Recalculando próximo ciclo después de reinicio...")
                print(f"   - Tiempo actual (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   - Tiempo de espera: {TIEMPO_ESPERA}s ({TIEMPO_ESPERA/60:.1f} minutos)")
                print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
                send_status_update_with_next_cycle('running', next_cycle)
                print(f"✅ Próximo ciclo recalculado y enviado al servidor correctamente")
            except Exception as e:
                print(f"⚠️  Error al recalcular/enviar próxima hora del ciclo: {e}")
                import traceback
                traceback.print_exc()
            use_local = ub.get_use_local_accounts()
            if use_local:
                local_count = ub.get_cookie_count()
                if local_count == 0:
                    print("⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor...")
                    use_local = False
                else:
                    print(f"📦 Usando {local_count} cuentas de la base de datos local")
            if not use_local:
                ub.clear_database()
                print(f"📡 Obteniendo {MAX_ITERATIONS} cuentas del servidor...")
                accounts = ub.fetch_accounts_from_server(MAX_ITERATIONS)
                if not accounts:
                    messagebox.showerror("Error", "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.")
                    break
                print(f"✅ Se obtuvieron {len(accounts)} nuevas cuentas del servidor")
                ub.save_cookies_to_db(accounts)
            iteration_count = 0
            ub.last_cookie_id = 1
            continue
        iteration_count += 1
        if not self.running:
            print("🛑 Bot detenido durante el bucle principal")
            break
        print(f"🔄 Iteración {iteration_count}/{MAX_ITERATIONS}: Procesando cuenta {ub.last_cookie_id}...")
        ub.click_add_account()
        for _ in range(20):
            if not self.running:
                break
            time.sleep(0.5)
        if not self.running:
            print("🛑 Bot detenido después de agregar cuenta")
            break
        if not self.safe_sleep(0.5):
            break
        ub.click_europa_boton()
        if not self.safe_sleep(0.5):
            break
        ub.click_europa_boton2()
        if not self.safe_sleep(2):
            break
        if not ub.wait_for_linkedin_detected(max_attempts=8, wait_time=1, confidence=0.7):
            print(f"⚠️ LinkedIn no detectado para cuenta {ub.last_cookie_id}, reintentando...")
            continue
        ub.click_add_cookie()
        if not self.safe_sleep(2):
            break
        if not self.safe_sleep(0.5):
            break
        ub.click_europa_boton()
        if not self.safe_sleep(0.5):
            break
        ub.click_europa_boton2()
        if not self.safe_sleep(0.5):
            break
        if not ub.find_and_click_input():
            print(f"❌ Error al procesar cuenta {ub.last_cookie_id}, continuando con la siguiente...")
            ub.last_cookie_id += 1
            continue
        print(f"✅ Cuenta {ub.last_cookie_id} procesada exitosamente ({iteration_count}/{MAX_ITERATIONS})")
        if not self.safe_sleep(5):
            break
        ub.last_cookie_id += 1
