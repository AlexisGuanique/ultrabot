import sqlite3
import json
import shutil
import time
import sys
import os
import glob
import re


# ── Configuración ────────────────────────────────────────────────────
SQLITE_BASE  = "1"              # Archivo SQLite base (Chrome Cookies)
JSON_FOLDER  = "."              # Carpeta donde están los archivos
JSON_PATTERN = "*.txt"          # Patrón de archivos a procesar
OUTPUT_NAME  = "Cookies"        # Nombre del archivo final en cada carpeta
OUTPUT_BASE  = "output"         # Prefijo carpetas: output_001, output_002...
# ─────────────────────────────────────────────────────────────────────

def extract_cookies_from_line(line):
    """Extrae el array JSON de cookies de una línea con formato mixto.
    Soporta:
      - Línea pura JSON: [{...}]
      - Línea mixta:  UserAgent\\tEmail\\tPassword\\t[{...}]
    """
    line = line.strip()
    if not line:
        return None

    # Buscar el primer '[' que inicie un array JSON de cookies
    match = re.search(r'(\[{.*)\Z', line, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Intentar parsear la línea completa como JSON
    try:
        data = json.loads(line)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    return None

def load_cookies(filepath):
    """Carga todas las cookies de un archivo.
    Soporta:
      - JSON puro (array)
      - Archivo con múltiples líneas, cada una con formato mixto
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Intentar como JSON puro primero
    try:
        data = json.loads(content)
        if isinstance(data, list) and len(data) > 0:
            # Si es lista de cookies directamente
            if isinstance(data[0], dict) and "name" in data[0]:
                return [(None, data)]  # (info_extra, cookies)
        return [(None, data if isinstance(data, list) else [data])]
    except json.JSONDecodeError:
        pass

    # Procesar línea por línea (formato mixto)
    results = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("=") or line.startswith("Total") or line.startswith("Formato") or line.startswith("CUENTAS"):
            continue

        cookies = extract_cookies_from_line(line)
        if cookies:
            # Extraer info extra (User-Agent, Email, Password) si existe
            parts = line.split("\t")
            info = None
            if len(parts) >= 3:
                info = {
                    "user_agent": parts[0] if len(parts) > 0 else "",
                    "email":      parts[1] if len(parts) > 1 else "",
                    "password":   parts[2] if len(parts) > 2 else "",
                }
            results.append((info, cookies))

    return results

def insert_cookies(conn, cookies, now_us, epoch_diff, samesite_map):
    """Inserta una lista de cookies. Retorna (inserted, skipped, errors)."""
    c = conn.cursor()
    inserted = skipped = errors = 0

    for ck in cookies:
        try:
            host        = ck.get("domain", "")
            name        = ck.get("name", "")
            value       = ck.get("value", "")
            path        = ck.get("path", "/")
            is_secure   = 1 if ck.get("secure")   else 0
            is_httponly = 1 if ck.get("httpOnly")  else 0

            exp           = ck.get("expirationDate")
            expires_utc   = int(exp * 1_000_000) + epoch_diff if exp else 0
            has_expires   = 1 if exp else 0
            is_persistent = 0 if ck.get("session") else 1

            samesite      = samesite_map.get(ck.get("sameSite"), -1)
            source_scheme = 2 if is_secure else 1
            source_port   = 443 if is_secure else 80

            pk        = ck.get("partitionKey") or {}
            top_frame = pk.get("topLevelSite", "") or ""
            has_cross = 1 if pk.get("hasCrossSiteAncestor") else 0

            c.execute("""
                INSERT OR IGNORE INTO cookies (
                    creation_utc, host_key, top_frame_site_key, name, value,
                    encrypted_value, path, expires_utc, is_secure, is_httponly,
                    last_access_utc, has_expires, is_persistent, priority,
                    samesite, source_scheme, source_port, last_update_utc,
                    source_type, has_cross_site_ancestor
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                now_us, host, top_frame, name, value,
                b"", path, expires_utc, is_secure, is_httponly,
                now_us, has_expires, is_persistent, 1,
                samesite, source_scheme, source_port, now_us,
                0, has_cross
            ))

            if c.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        except Exception as e:
            errors += 1
            print(f"      [ERR] {ck.get('name', '?')}: {e}")

    return inserted, skipped, errors

def process_file(json_path, base_index):
    """Procesa un archivo y genera una carpeta output_NNN por cada cuenta encontrada."""
    EPOCH_DIFF_US = 11644473600 * 1_000_000
    now_us = int(time.time() * 1_000_000) + EPOCH_DIFF_US
    samesite_map = {
        "no_restriction": 0, "lax": 1, "strict": 2, "none": -1, None: -1
    }

    entries = load_cookies(json_path)
    print(f"   Cuentas/entradas encontradas: {len(entries)}")

    results = []

    for i, (info, cookies) in enumerate(entries):
        folder_name = f"{OUTPUT_BASE}_{base_index + i:03d}"
        os.makedirs(folder_name, exist_ok=True)
        output_file = os.path.join(folder_name, OUTPUT_NAME)

        shutil.copy(SQLITE_BASE, output_file)

        conn = sqlite3.connect(output_file)
        inserted, skipped, errors = insert_cookies(conn, cookies, now_us, EPOCH_DIFF_US, samesite_map)
        conn.commit()

        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM cookies")
        total = cur.fetchone()[0]
        conn.close()

        email = info["email"] if info else "—"
        print(f"   [{folder_name}] {email} → OK:{inserted} DUP:{skipped} ERR:{errors} | Total:{total}")

        results.append({
            "folder":   folder_name,
            "email":    email,
            "inserted": inserted,
            "skipped":  skipped,
            "errors":   errors,
            "total":    total,
        })

    return results

def main():
    if not os.path.exists(SQLITE_BASE):
        print(f"[ERROR] No se encontró el archivo base: {SQLITE_BASE}")
        sys.exit(1)

    pattern   = os.path.join(JSON_FOLDER, JSON_PATTERN)
    all_files = sorted(glob.glob(pattern))

    script_name = os.path.basename(__file__)
    json_files  = [
        f for f in all_files
        if os.path.isfile(f)
        and os.path.basename(f) != script_name
        and os.path.basename(f) != SQLITE_BASE
        and os.path.basename(f) != OUTPUT_NAME
        and not os.path.dirname(os.path.abspath(f)).startswith(
            os.path.abspath(OUTPUT_BASE)
        )
    ]

    if not json_files:
        print(f"[ERROR] No se encontraron archivos con el patrón: {pattern}")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"  Cookie Converter — Multi-archivo / Multi-cuenta")
    print(f"{'='*60}")
    print(f"  Archivos a procesar: {len(json_files)}")
    print(f"{'='*60}\n")

    all_results = []
    folder_index = 1

    for jf in json_files:
        print(f"[ARCHIVO] {os.path.basename(jf)}")
        try:
            results = process_file(jf, folder_index)
            all_results.extend(results)
            folder_index += len(results)
        except Exception as e:
            print(f"   [FALLO] {e}")
        print()

    # Resumen
    print(f"\n{'='*60}")
    print(f"  RESUMEN FINAL — {len(all_results)} carpetas generadas")
    print(f"{'='*60}")
    print(f"  {'Carpeta':<14} {'Email':<35} {'Ins':>4} {'Dup':>4} {'Tot':>5}")
    print(f"  {'─'*65}")
    for r in all_results:
        email_short = r['email'][:33] + ".." if len(r['email']) > 35 else r['email']
        print(f"  {os.path.basename(r['folder']):<14} {email_short:<35} {r['inserted']:>4} {r['skipped']:>4} {r['total']:>5}")
    print(f"{'='*60}")
    print(f"\n  Cada carpeta output_NNN/ contiene el archivo '{OUTPUT_NAME}'.")

if __name__ == "__main__":
    main()