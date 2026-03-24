"""
Convierte cookies JSON (BD del proyecto) al SQLite Chromium ``Cookies`` dentro de cada
``.../Partitions/<id>/Network/``.

- No crea carpetas ``output_*``: escribe directamente ``Network/Cookies``.
- Si ya existe ``Cookies`` en esa carpeta, lo sustituye (sin carpeta intermedia).
- Si no existe, parte de la plantilla ``app/helpers/Cookies`` (mismo esquema SQLite).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time

# Nombre del archivo en cada carpeta Network (Chromium)
OUTPUT_NAME = "Cookies"


def _cookies_db_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "app", "database", "cookies.db")


def get_helper_cookies_template_path() -> str:
    """
    Plantilla SQLite vacía: ``app/helpers/Cookies``.

    Con PyInstaller ``--onefile``, los datos van a ``sys._MEIPASS``; hay que incluir el
    archivo con ``--add-data "app/helpers/Cookies;app/helpers"`` (Windows) o la variante
    con ``:`` según la documentación de tu plataforma.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = os.path.join(sys._MEIPASS, "app", "helpers", "Cookies")
        if os.path.isfile(p):
            return p
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cookies")


def fetch_cookie_records_from_app_db():
    """Filas de la tabla cookies: id, cookie, email, password, user_agent."""
    db_path = _cookies_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, cookie, email, password, user_agent FROM cookies ORDER BY id"
        )
        rows = cur.fetchall()
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


def extract_cookies_from_line(line: str):
    line = line.strip()
    if not line:
        return None
    match = re.search(r"(\[{.*)\Z", line, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    try:
        data = json.loads(line)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass
    return None


def parse_cookie_text_to_entries(content: str) -> list:
    content = content.strip()
    if not content:
        return []
    try:
        data = json.loads(content)
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict) and "name" in data[0]:
                return [(None, data)]
        return [(None, data if isinstance(data, list) else [data])]
    except json.JSONDecodeError:
        pass
    results = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("=") or line.startswith("Total"):
            continue
        cookies = extract_cookies_from_line(line)
        if cookies:
            parts = line.split("\t")
            info = None
            if len(parts) >= 3:
                info = {
                    "user_agent": parts[0] if len(parts) > 0 else "",
                    "email": parts[1] if len(parts) > 1 else "",
                    "password": parts[2] if len(parts) > 2 else "",
                }
            results.append((info, cookies))
    return results


def parse_record_to_cookie_list(record: dict) -> list | None:
    text = (record.get("cookie") or "").strip()
    if not text:
        return None
    parsed = parse_cookie_text_to_entries(text)
    if not parsed:
        return None
    _info, cookies = parsed[0]
    return cookies


def clear_chromium_cookies_table(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cookies")


def _remove_sqlite_sidecars(base_file_path: str) -> None:
    for ext in ("-journal", "-wal", "-shm"):
        p = base_file_path + ext
        if os.path.isfile(p):
            try:
                os.remove(p)
            except OSError:
                pass


def insert_cookies(conn, cookies, now_us, epoch_diff, samesite_map):
    c = conn.cursor()
    inserted = skipped = errors = 0
    for ck in cookies:
        try:
            host = ck.get("domain", "")
            name = ck.get("name", "")
            value = ck.get("value", "")
            path = ck.get("path", "/")
            is_secure = 1 if ck.get("secure") else 0
            is_httponly = 1 if ck.get("httpOnly") else 0
            exp = ck.get("expirationDate")
            expires_utc = int(exp * 1_000_000) + epoch_diff if exp else 0
            has_expires = 1 if exp else 0
            is_persistent = 0 if ck.get("session") else 1
            samesite = samesite_map.get(ck.get("sameSite"), -1)
            source_scheme = 2 if is_secure else 1
            source_port = 443 if is_secure else 80
            pk = ck.get("partitionKey") or {}
            top_frame = pk.get("topLevelSite", "") or ""
            has_cross = 1 if pk.get("hasCrossSiteAncestor") else 0
            c.execute(
                """
                INSERT OR IGNORE INTO cookies (
                    creation_utc, host_key, top_frame_site_key, name, value,
                    encrypted_value, path, expires_utc, is_secure, is_httponly,
                    last_access_utc, has_expires, is_persistent, priority,
                    samesite, source_scheme, source_port, last_update_utc,
                    source_type, has_cross_site_ancestor
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    now_us,
                    host,
                    top_frame,
                    name,
                    value,
                    b"",
                    path,
                    expires_utc,
                    is_secure,
                    is_httponly,
                    now_us,
                    has_expires,
                    is_persistent,
                    1,
                    samesite,
                    source_scheme,
                    source_port,
                    now_us,
                    0,
                    has_cross,
                ),
            )
            if c.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            errors += 1
            print(f"      [ERR] {ck.get('name', '?')}: {e}")
    return inserted, skipped, errors


def write_chrome_cookies_sqlite(dest_path: str, cookies: list) -> dict:
    """
    Escribe ``dest_path`` (ruta completa a .../Network/Cookies).

    - Si ``dest_path`` ya existe: se usa como base (perfil), se vacía la tabla y se insertan datos.
      Mensaje: sustitución directa (equivalente a confirmar "sí").
    - Si no existe: se copia la plantilla ``app/helpers/Cookies`` y luego se insertan datos.

    No crea carpetas ``output_*``; solo asegura que exista el directorio ``Network``.
    """
    dest_path = os.path.abspath(dest_path)
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)

    tpl = get_helper_cookies_template_path()
    if not os.path.isfile(tpl):
        raise FileNotFoundError(
            f"Falta la plantilla SQLite en: {tpl}\n"
            "  Copia un archivo Cookies vacío de Chromium y colócalo como app/helpers/Cookies"
        )

    replacing = os.path.isfile(dest_path)
    if replacing:
        print(f"      → Sustituyendo Cookies existente: {dest_path}")
    else:
        print(f"      → Creando Cookies desde plantilla (no existía el archivo): {dest_path}")

    fd, tmp = tempfile.mkstemp(suffix=".tmp", prefix="cookies_", dir=dest_dir)
    os.close(fd)
    try:
        if replacing:
            shutil.copy2(dest_path, tmp)
        else:
            shutil.copy2(tpl, tmp)

        conn = sqlite3.connect(tmp)
        clear_chromium_cookies_table(conn)
        EPOCH_DIFF_US = 11644473600 * 1_000_000
        now_us = int(time.time() * 1_000_000) + EPOCH_DIFF_US
        samesite_map = {"no_restriction": 0, "lax": 1, "strict": 2, "none": -1, None: -1}
        inserted, skipped, errors = insert_cookies(conn, cookies, now_us, EPOCH_DIFF_US, samesite_map)
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM cookies")
        total = cur.fetchone()[0]
        conn.close()

        _remove_sqlite_sidecars(dest_path)
        if replacing and os.path.isfile(dest_path):
            os.remove(dest_path)
        shutil.move(tmp, dest_path)
    except Exception:
        if os.path.isfile(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise

    return {
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
        "total": total,
    }


def main():
    from app.ultrabot.cookie_convert import sync_ultra_partitions_network_cookies

    code = sync_ultra_partitions_network_cookies()
    sys.exit(0 if code >= 0 else 1)


if __name__ == "__main__":
    main()
