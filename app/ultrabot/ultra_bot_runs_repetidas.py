"""
Flujo de cuentas repetidas: con ultra_login_mode=ui se usa la interfaz de Ultra para cookies;
con sqlite se replica run_ultra_bot_sqlite_thread (Partitions + sync Cookies en disco).
Carga de cuentas local o servidor según get_use_local_accounts().
"""
from __future__ import annotations

import time
from typing import Optional
from tkinter import messagebox

from app.database.database import (
    expand_cookies_in_db_for_repetidas,
    get_repetidas_settings,
    replace_cookies_table_rows,
    snapshot_cookie_rows_ordered,
    truncate_cookies_to_first_n,
)

import app.ultrabot.ultra_bot as ub

# Misma ventana de sondeo que en el flujo sqlite/UI antes de acciones críticas
_LINKEDIN_CARGA_POLL_INTERVAL = 0.5
_LINKEDIN_CARGA_POLL_SECONDS = 20.0


def _poll_linkedin_carga_bien(thread, label: str) -> bool:
    """Espera hasta ~20s a que linkedincargabien sea visible; respeta thread.running."""
    print(
        f"  🔍 {label} — buscando {ub.LINKEDIN_CARGA_BIEN_IMAGE} "
        f"(hasta {_LINKEDIN_CARGA_POLL_SECONDS:.0f}s)..."
    )
    _polls = max(1, int(_LINKEDIN_CARGA_POLL_SECONDS / _LINKEDIN_CARGA_POLL_INTERVAL))
    for _ in range(_polls):
        if not thread.running:
            return False
        if ub.linkedin_carga_bien_visible(confidence=0.65):
            print("  ✅ linkedincargabien detectado.")
            return True
        if not thread.safe_sleep(_LINKEDIN_CARGA_POLL_INTERVAL):
            return False
    return False


def _load_accounts_for_repetidas_batch(ACCOUNTS_TO_REPEAT: int) -> Optional[int]:
    """
    Resuelve cuántas cuentas procesar en este ciclo (orden de id en BD: 1..N).
    Modo local: no limpia BD; usa hasta ACCOUNTS_TO_REPEAT filas existentes.
    Modo servidor: limpia BD, pide cuentas al servidor y guarda.
    Devuelve None si falla (y muestra mensaje cuando aplica).
    """
    use_local = ub.get_use_local_accounts()
    if use_local:
        local_count = ub.get_cookie_count()
        if local_count == 0:
            print(
                "⚠️ No hay cuentas en la base de datos local. Cambiando a modo servidor..."
            )
            use_local = False
        else:
            total = min(ACCOUNTS_TO_REPEAT, local_count)
            if local_count < ACCOUNTS_TO_REPEAT:
                print(
                    f"⚠️ Solo hay {local_count} cuentas locales; se procesarán {total} "
                    f"(config repetidas pedía hasta {ACCOUNTS_TO_REPEAT})."
                )
            print(
                f"📦 Repetidas: usando {total} cuenta(s) de la base de datos local"
            )
            ub.last_cookie_id = 1
            return total

    print("🗑️ Limpiando base de datos...")
    ub.clear_database()
    print(f"📡 Obteniendo {ACCOUNTS_TO_REPEAT} cuentas del servidor...")
    accounts = ub.fetch_accounts_from_server(ACCOUNTS_TO_REPEAT)
    if not accounts:
        messagebox.showerror(
            "Error",
            "No se pudieron obtener cuentas del servidor. Verifica tu conexión y credenciales.",
        )
        return None
    print(f"✅ Se obtuvieron {len(accounts)} cuentas del servidor")
    ub.save_cookies_to_db(accounts)
    saved_count = ub.get_cookie_count()
    if saved_count == 0:
        messagebox.showerror(
            "Error",
            f"No se pudieron guardar las cuentas en la base de datos. "
            f"Se obtuvieron {len(accounts)} cuentas pero no se guardaron.",
        )
        return None
    print(f"✅ Se guardaron {saved_count} cuentas en la base de datos")
    ub.last_cookie_id = 1
    return len(accounts)


def _repetidas_login_preamble(thread) -> bool:
    """Logo → login → verificación Ultra. False = abortar el flujo repetidas."""
    self = thread
    print("🚀 Iniciando UltraBot Repetidas...")
    if not self.safe_sleep(3):
        print("🛑 Bot detenido antes de comenzar")
        return False
    if not self.running:
        return False

    print("🖱️ Buscando logo de Ultra...")
    if not ub.click_ultra_logo(max_attempts=5, delay_between_attempts=2):
        messagebox.showerror(
            "Error",
            "No se pudo hacer clic en el logo de Ultra después de varios intentos. Verifica que Ultra esté disponible.",
        )
        return False

    print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
    if not self.safe_sleep(40):
        print("🛑 Bot detenido durante espera inicial")
        return False

    print("🔐 Iniciando proceso de login en Ultra...")
    if not ub.login_with_ultra_credentials():
        return False

    if not self.running:
        print("🛑 Bot detenido después de login")
        return False

    print("✅ Login exitoso en Ultra")
    print("⏳ Esperando 15 segundos después del login...")
    if not self.safe_sleep(15):
        print("🛑 Bot detenido durante espera post-login")
        return False

    print("\n🔍 Verificando que Ultra haya cargado correctamente...")
    if not ub.check_ultra_error_and_recover(max_attempts=5):
        print("❌ Ultra no cargó correctamente después de múltiples intentos")
        messagebox.showerror(
            "Error de Ultra",
            "Ultra no está cargando correctamente después del login. El proceso se detendrá.",
        )
        return False

    if not self.running:
        print("🛑 Bot detenido después de verificación de errores de Ultra")
        return False

    print("✅ Ultra cargó correctamente, continuando con repetidas...")
    return True


def _repetidas_load_config():
    config = get_repetidas_settings()
    if config:
        return (
            config["accounts_to_repeat"],
            config["repetitions_count"],
            config["interval_seconds"],
        )
    return 5, 3, 7200


def _repetidas_sqlite_open_tabs_kill_sync(self, batch_size: int) -> Optional[int]:
    """
    Config interna → pestañas → cierre → kill → espera Partitions → sync Cookies.
    Devuelve n_sync o None si falla.
    """
    print(
        f"\n🔄 Repetidas (Partitions): lote de {batch_size} pestaña(s) — "
        "fila i (ORDER BY id) → partición i (orden creación)."
    )
    ub.click_ultra_internal_config()

    time.sleep(2)
    for tab_i in range(batch_size):
        if not self.running:
            return None
        ub.click_add_account()
        if tab_i < batch_size - 1:
            time.sleep(2)

    if not self.running:
        return None
    time.sleep(5)
    if not self.safe_sleep(2):
        return None
    ub.click_coordinates(1339, 10)

    if not self.safe_sleep(2):
        return None

    print("⏳ Esperando antes de forzar cierre de procesos de Ultra...")
    if not self.safe_sleep(4):
        return None

    try:
        ub.kill_ultra_processes(show_confirmation=False)
    except Exception as e:
        print(f"⚠️ Error al terminar procesos de Ultra (continuando): {e}")
        import traceback

        traceback.print_exc()

    print("⏳ Esperando a que el sistema libere los archivos Cookies...")
    if not self.safe_sleep(5):
        return None

    print(
        "⏳ Esperando a que existan carpetas en Partitions (puede tardar unos segundos)..."
    )
    if not self.safe_sleep(5):
        return None

    n_db = ub.get_cookie_count()
    PARTITION_POLL_INTERVAL = 3.0
    PARTITION_POLL_MAX_ROUNDS = 20
    n_part = 0
    for poll_round in range(PARTITION_POLL_MAX_ROUNDS):
        if not self.running:
            return None
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
                return None

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
        return None

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
        return None

    print("\n📂 Sincronizando archivos Cookies en cada carpeta Network desde la base de datos...")
    sync_code = ub.sync_ultra_partitions_network_cookies()
    if sync_code < 0:
        print("❌ No se pudo completar la sincronización de cookies en disco.")
        return None

    print(
        "\n✅ Cookies escritas en disco. Pasando a activación de cuentas (proceso de tabs)..."
    )
    return n_sync


def _repetidas_sqlite_wait_linkedin_pre_start(self) -> bool:
    """Mismo criterio que run_ultra_bot_sqlite_thread antes de Start all tabs."""
    LINKEDIN_PRE_START_MAX_RETRIES = 5
    POLL_INTERVAL = 0.5
    POLL_SECONDS_PER_ATTEMPT = 20.0
    activation_ready = False
    for load_attempt in range(LINKEDIN_PRE_START_MAX_RETRIES):
        if not self.running:
            return False
        if load_attempt > 0:
            print(
                f"🔄 Reintentando detección de linkedincargabien "
                f"({load_attempt + 1}/{LINKEDIN_PRE_START_MAX_RETRIES})..."
            )

        ub.click_europa_boton()
        if not self.safe_sleep(1):
            return False
        ub.click_europa_boton2()
        if not self.safe_sleep(2):
            return False

        print(
            f"🔍 Buscando {ub.LINKEDIN_CARGA_BIEN_IMAGE} (hasta {POLL_SECONDS_PER_ATTEMPT:.0f}s)..."
        )
        _polls = max(1, int(POLL_SECONDS_PER_ATTEMPT / POLL_INTERVAL))
        seen_linkedin = False
        for _ in range(_polls):
            if not self.running:
                return False
            if ub.linkedin_carga_bien_visible(confidence=0.65):
                print("✅ linkedincargabien detectado. Continuando con Start all tabs...")
                seen_linkedin = True
                break
            if not self.safe_sleep(POLL_INTERVAL):
                return False

        if seen_linkedin:
            activation_ready = True
            break

        print(
            "⚠️ No se detectó linkedincargabien; cerrando Ultra, reabriendo y "
            f"esperando 30 s antes de volver a verificar..."
        )
        if load_attempt >= LINKEDIN_PRE_START_MAX_RETRIES - 1:
            break

        ub.click_coordinates(1339, 10)
        print("⏳ Esperando 5 s tras cerrar la ventana antes de terminar procesos de Ultra...")
        if not self.safe_sleep(5):
            return False
        try:
            ub.kill_ultra_processes(show_confirmation=False)
        except Exception as e:
            print(f"⚠️ Error al terminar procesos de Ultra: {e}")
            import traceback

            traceback.print_exc()

        print("🔄 Abriendo Ultra de nuevo (logo)...")
        if not ub.click_ultra_logo(max_attempts=3, delay_between_attempts=1):
            print("❌ No se pudo hacer clic en el logo de Ultra")
            return False

        print("⏳ Esperando 30 s para que Ultra estabilice tras reabrir...")
        if not self.safe_sleep(30):
            return False

        if not ub.check_ultra_error_and_recover(max_attempts=5):
            print(
                "⚠️ Ultra no pasó la verificación tras el reinicio; se intentará de nuevo..."
            )

    if not activation_ready:
        if self.running:
            messagebox.showerror(
                "LinkedIn / Ultra",
                "No se pudo detectar linkedincargabien.PNG después de varios intentos.\n\n"
                "No se ejecutará Start all tabs.",
            )
        return False
    return True


def _repetidas_sqlite_run_tabs_cycle_repetidas(
    self, work_batch: int, TIEMPO_ESPERA: int
) -> bool:
    """Logo → 600s → linkedincargabien → Start all tabs → espera → stop → ventanas → cache → login."""
    ub.click_ultra_logo()
    if not self.safe_sleep(3):
        return False
    time.sleep(600)

    if not _repetidas_sqlite_wait_linkedin_pre_start(self):
        return False

    print(f"▶️ Iniciando todas las tabs (repetidas SQLite) y esperando {TIEMPO_ESPERA}s...")
    if not self.safe_sleep(2):
        return False
    ub.click_start_all_tabs()
    if not self.safe_sleep(2):
        return False
    ub.click_europa_boton()
    if not self.safe_sleep(1):
        return False
    ub.click_europa_boton2()

    if not ub.click_acept_actionTabs():
        if not self.safe_sleep(1):
            return False
        ub.click_acept_actionTabs()

    if not self.safe_sleep(TIEMPO_ESPERA):
        print("🛑 Bot detenido durante espera entre tabs (repetidas SQLite)")
        return False
    print("⏹️ Tiempo de espera completado, deteniendo tabs...")

    ub.click_europa_boton()
    if not self.safe_sleep(1):
        return False
    ub.click_europa_boton2()

    ub.click_stop_all_tabs()
    if not self.safe_sleep(2):
        return False

    if not ub.click_acept_stop_actionTabs():
        if not self.safe_sleep(1):
            return False
        ub.click_acept_stop_actionTabs()
        if not self.safe_sleep(2):
            return False

    if not self.safe_sleep(2):
        return False
    print(f"🗑️ Cerrando {work_batch} ventanas...")
    for _ in range(work_batch):
        if not self.running:
            break
        ub.click_close_window()
        if not self.safe_sleep(0.5):
            return False

    if not self.running:
        return False

    ub.click_coordinates(1339, 10)
    if not self.safe_sleep(5):
        return False

    print("🔪 Eliminando procesos de Ultra...")
    try:
        ub.kill_ultra_processes(show_confirmation=False)
    except Exception as e:
        print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")

    print("🗑️ Eliminando cache de Ultra...")
    cache_deleted = False
    max_cache_attempts = 3

    for cache_attempt in range(max_cache_attempts):
        cache_deleted = ub.handle_delete_ultra_folder(
            show_confirmation=False, max_wait_time=45
        )

        if cache_deleted:
            print("✅ Cache eliminada exitosamente")
            break
        print(f"⚠️ Intento {cache_attempt + 1}/{max_cache_attempts} de eliminar cache falló")
        if cache_attempt < max_cache_attempts - 1:
            if not self.safe_sleep(5):
                return False
            try:
                ub.kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")

    if not cache_deleted:
        messagebox.showerror(
            "Error",
            "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.",
        )
        return False

    print("🔄 Reintentando login después de limpieza...")
    max_restart_attempts = 3
    login_successful = False

    for restart_attempt in range(max_restart_attempts):
        print(f"  🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
        if ub.click_ultra_logo():
            print("⏳ Esperando 40 segundos para que Ultra se abra completamente...")
            time.sleep(40)
            if ub.wait_for_login_interface(max_attempts=3, wait_time=15):
                if ub.login_with_ultra_credentials():
                    time.sleep(2)
                    login_successful = True
                    break
                login_successful = False
                break
            if restart_attempt < max_restart_attempts - 1:
                ub.click_coordinates(1339, 10)
                time.sleep(5)
                try:
                    ub.kill_ultra_processes(show_confirmation=False)
                except Exception as e:
                    print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)
        elif restart_attempt < max_restart_attempts - 1:
            ub.click_coordinates(1339, 10)
            time.sleep(5)
            try:
                ub.kill_ultra_processes(show_confirmation=False)
            except Exception as e:
                print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
            ub.handle_delete_ultra_folder(show_confirmation=False, max_wait_time=30)

    if not login_successful:
        messagebox.showerror(
            "Error",
            "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.",
        )
        return False

    try:
        from datetime import datetime, timedelta
        from app.auth.auth import send_status_update_with_next_cycle

        next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
        print("📅 Recalculando próximo ciclo después de reinicio (repetidas SQLite)...")
        print(f"   - Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
        send_status_update_with_next_cycle("running", next_cycle)
        print("✅ Próximo ciclo recalculado y enviado al servidor correctamente")
    except Exception as e:
        print(f"⚠️  Error al recalcular/enviar próxima hora del ciclo: {e}")
        import traceback

        traceback.print_exc()

    print("🔄 Reiniciando ciclo de repetidas (SQLite)...")
    return True


def run_ultra_bot_repetidas_sqlite_thread(thread) -> None:
    """
    Repetidas con flujo Partitions igual que run_ultra_bot_sqlite_thread: cuentas base ×
    repeticiones = pestañas; sync de Cookies en disco; activación sin UI de cookies.
    """
    self = thread
    if not _repetidas_login_preamble(self):
        return

    ACCOUNTS_TO_REPEAT, REPETITIONS_COUNT, TIEMPO_ESPERA = _repetidas_load_config()

    print("📂 Modo repetidas: logueo SQLite / Partitions (cookies desde BD, no por interfaz).")
    if ub.get_use_local_accounts():
        print("📦 Modo cuentas: base de datos local (repetidas SQLite)")
    else:
        print("🌐 Modo cuentas: servidor (repetidas SQLite)")

    print(
        f"⚙️ Repetidas (SQLite): hasta {ACCOUNTS_TO_REPEAT} cuentas base, "
        f"{REPETITIONS_COUNT} repeticiones → hasta {ACCOUNTS_TO_REPEAT * REPETITIONS_COUNT} pestañas, "
        f"{TIEMPO_ESPERA}s de espera tras Start all tabs"
    )

    try:
        from datetime import datetime, timedelta
        from app.auth.auth import send_status_update_with_next_cycle

        next_cycle = datetime.utcnow() + timedelta(seconds=TIEMPO_ESPERA)
        print(f"📅 Próximo ciclo (UTC): {next_cycle.strftime('%Y-%m-%d %H:%M:%S')}")
        send_status_update_with_next_cycle("running", next_cycle)
        print("✅ Próximo ciclo enviado al servidor correctamente")
    except Exception as e:
        print(f"⚠️  Error al calcular/enviar próxima hora del ciclo: {e}")
        import traceback

        traceback.print_exc()

    while self.running:
        n_base = _load_accounts_for_repetidas_batch(ACCOUNTS_TO_REPEAT)
        if n_base is None:
            break
        if ub.get_cookie_count() > n_base:
            truncate_cookies_to_first_n(n_base)

        base_rows_snapshot = snapshot_cookie_rows_ordered()
        if len(base_rows_snapshot) != n_base:
            print(
                f"⚠️ Se esperaban {n_base} filas base tras la carga; "
                f"hay {len(base_rows_snapshot)}. Se continúa con las actuales."
            )

        if not expand_cookies_in_db_for_repetidas(REPETITIONS_COUNT):
            messagebox.showerror(
                "Error",
                "No se pudo expandir las cookies en la base de datos para las repeticiones.",
            )
            replace_cookies_table_rows(base_rows_snapshot)
            break

        batch_size = ub.get_cookie_count()
        expected = n_base * REPETITIONS_COUNT
        if batch_size != expected:
            print(
                f"⚠️ Filas en BD ({batch_size}) ≠ esperado {n_base}×{REPETITIONS_COUNT}={expected}. "
                f"Se usa batch_size={batch_size}."
            )

        try:
            n_sync = _repetidas_sqlite_open_tabs_kill_sync(self, batch_size)
            if n_sync is None:
                break
            if not _repetidas_sqlite_run_tabs_cycle_repetidas(self, n_sync, TIEMPO_ESPERA):
                break
        finally:
            replace_cookies_table_rows(base_rows_snapshot)


def run_ultra_bot_repetidas_thread(thread) -> None:
    self = thread
    if not _repetidas_login_preamble(self):
        return

    ACCOUNTS_TO_REPEAT, REPETITIONS_COUNT, TIEMPO_ESPERA = _repetidas_load_config()

    if ub.get_use_local_accounts():
        print("📦 Modo cuentas: base de datos local (repetidas)")
    else:
        print("🌐 Modo cuentas: servidor (repetidas)")

    print(
        f"⚙️ Configuración Repetidas: hasta {ACCOUNTS_TO_REPEAT} cuentas, "
        f"{REPETITIONS_COUNT} repeticiones, {TIEMPO_ESPERA}s de espera"
    )

    while self.running:
        total_accounts = _load_accounts_for_repetidas_batch(ACCOUNTS_TO_REPEAT)
        if total_accounts is None:
            break

        print(
            f"🔄 Procesando {total_accounts} cuentas con {REPETITIONS_COUNT} repeticiones cada una..."
        )

        for account_index in range(total_accounts):
            if not self.running:
                break

            current_cookie_id = account_index + 1
            print(f"📋 Procesando cuenta {current_cookie_id}/{total_accounts}...")

            for repetition in range(REPETITIONS_COUNT):
                if not self.running:
                    break

                print(
                    f"  🔁 Repetición {repetition + 1}/{REPETITIONS_COUNT} de cuenta {current_cookie_id}..."
                )
                ub.click_add_account()
                if not self.safe_sleep(10):
                    break
                if not self.running:
                    break

                if not self.safe_sleep(0.5):
                    break
                ub.click_europa_boton()
                if not self.safe_sleep(0.5):
                    break
                ub.click_europa_boton2()
                if not self.safe_sleep(2):
                    break

                if not ub.wait_for_linkedin_detected(
                    max_attempts=8, wait_time=1, confidence=0.7
                ):
                    print(
                        f"  ⚠️ LinkedIn no detectado para cuenta {current_cookie_id}, "
                        f"repetición {repetition + 1}, reintentando desde click_add_account()..."
                    )
                    continue

                if not _poll_linkedin_carga_bien(
                    self,
                    f"Antes de agregar cookie (cuenta {current_cookie_id}, rep. {repetition + 1})",
                ):
                    if not self.running:
                        break
                    print(
                        f"  ⚠️ linkedincargabien no listo a tiempo; "
                        f"reintentando repetición {repetition + 1}..."
                    )
                    continue

                print(
                    f"  🍪 Agregando cookie para cuenta {current_cookie_id}, repetición {repetition + 1}..."
                )
                ub.click_add_cookie()
                if not self.safe_sleep(2):
                    break
                if not self.running:
                    break

                if not self.safe_sleep(0.5):
                    break
                ub.click_europa_boton()
                if not self.safe_sleep(0.5):
                    break
                ub.click_europa_boton2()
                if not self.safe_sleep(0.5):
                    break

                if not ub.find_and_click_input(cookie_id_override=current_cookie_id):
                    print(
                        f"  ❌ Error al procesar cookie para cuenta {current_cookie_id}, "
                        f"repetición {repetition + 1}"
                    )
                    continue

                print(
                    f"  ✅ Cookie procesada exitosamente para cuenta {current_cookie_id}, "
                    f"repetición {repetition + 1}"
                )
                if not self.safe_sleep(5):
                    break

        if not self.running:
            break

        ub.click_europa_boton()
        if not self.safe_sleep(1):
            break
        ub.click_europa_boton2()
        if not self.safe_sleep(2):
            break

        if not _poll_linkedin_carga_bien(self, "Antes de Start all tabs"):
            print(
                "⚠️ No se detectó linkedincargabien antes de Start all tabs; "
                "se intenta continuar (flujo repetidas)..."
            )

        print(f"▶️ Iniciando todas las tabs y esperando {TIEMPO_ESPERA}s...")
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

        if not self.safe_sleep(TIEMPO_ESPERA):
            print("🛑 Bot detenido durante espera entre tabs")
            break
        print("⏹️ Tiempo de espera completado, deteniendo tabs...")

        ub.click_europa_boton()
        if not self.safe_sleep(1):
            break
        ub.click_europa_boton2()

        ub.click_stop_all_tabs()
        if not self.safe_sleep(2):
            break

        if not ub.click_acept_stop_actionTabs():
            if not self.safe_sleep(1):
                break
            ub.click_acept_stop_actionTabs()
            if not self.safe_sleep(2):
                break

        if not self.safe_sleep(2):
            break
        total_windows = total_accounts * REPETITIONS_COUNT
        print(f"🗑️ Cerrando {total_windows} ventanas...")
        for _ in range(total_windows):
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

        print("🗑️ Eliminando cache de Ultra...")
        cache_deleted = False
        max_cache_attempts = 3

        for cache_attempt in range(max_cache_attempts):
            cache_deleted = ub.handle_delete_ultra_folder(
                show_confirmation=False, max_wait_time=45
            )

            if cache_deleted:
                print("✅ Cache eliminada exitosamente")
                break
            else:
                print(f"⚠️ Intento {cache_attempt + 1}/{max_cache_attempts} de eliminar cache falló")
                if cache_attempt < max_cache_attempts - 1:
                    if not self.safe_sleep(5):
                        break
                    try:
                        ub.kill_ultra_processes(show_confirmation=False)
                    except Exception as e:
                        print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")

        if not cache_deleted:
            messagebox.showerror(
                "Error",
                "No se pudo eliminar la cache de Ultra después de 3 intentos. El proceso se detendrá.",
            )
            break

        print("🔄 Reintentando login después de limpieza...")
        max_restart_attempts = 3
        login_successful = False

        for restart_attempt in range(max_restart_attempts):
            print(f"  🔄 Intento de reinicio {restart_attempt + 1}/{max_restart_attempts}...")
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
                        cache_deleted = ub.handle_delete_ultra_folder(
                            show_confirmation=False, max_wait_time=30
                        )
            else:
                if restart_attempt < max_restart_attempts - 1:
                    ub.click_coordinates(1339, 10)
                    time.sleep(5)
                    try:
                        ub.kill_ultra_processes(show_confirmation=False)
                    except Exception as e:
                        print(f"⚠️ Error al eliminar procesos de Ultra (continuando): {e}")
                    cache_deleted = ub.handle_delete_ultra_folder(
                        show_confirmation=False, max_wait_time=30
                    )

        if not login_successful:
            messagebox.showerror(
                "Error",
                "No se pudo completar el proceso de login después de varios intentos. Verifica que Ultra esté funcionando correctamente.",
            )
            break

        print("🔄 Reiniciando ciclo de repetidas...")
        # La siguiente vuelta del while vuelve a llamar a _load_accounts_for_repetidas_batch


