"""
Utilidades para recorrer Partitions de Ultra y listar el contenido de cada carpeta Network.

La ruta base coincide con app/ultrabot/utils_ultrabot.py (Roaming/Ultra).
"""

from __future__ import annotations

import argparse
import os
import sys

# Misma base que app/ultrabot/utils_ultrabot.py (USER_HOME + AppData/Roaming/Ultra)
USER_HOME = os.path.expanduser("~")
TARGET_FOLDER = os.path.join(USER_HOME, "AppData", "Roaming", "Ultra")

PARTITIONS_FOLDER_NAME = "Partitions"
NETWORK_FOLDER_NAME = "Network"


def get_ultra_partitions_path() -> str:
    """Ruta absoluta a .../AppData/Roaming/Ultra/Partitions."""
    return os.path.join(TARGET_FOLDER, PARTITIONS_FOLDER_NAME)


def get_partition_subfolder_names(
    partitions_path: str | None = None,
    *,
    sort_by: str = "alpha",
) -> list[str]:
    """
    Lista solo nombres de subcarpetas directas bajo Partitions (no archivos).

    Args:
        partitions_path: Ruta a Partitions o None para la ruta por defecto de Ultra.
        sort_by: Cómo ordenar las carpetas:
            - ``alpha``: orden alfabético (comportamiento histórico).
            - ``mtime_asc``: por fecha de modificación del directorio, más antigua primero
              (suele coincidir con el orden en que Ultra creó una partición por pestaña).
            - ``mtime_desc``: más reciente primero.

    Returns:
        Lista ordenada de nombres de directorio. Lista vacía si la ruta no existe o hay error.
    """
    base = partitions_path or get_ultra_partitions_path()
    if not os.path.isdir(base):
        return []

    names: list[str] = []
    try:
        for name in os.listdir(base):
            full = os.path.join(base, name)
            if os.path.isdir(full):
                names.append(name)
    except OSError:
        return []

    def _mtime_key(n: str) -> float:
        try:
            return os.path.getmtime(os.path.join(base, n))
        except OSError:
            return 0.0

    if sort_by == "mtime_asc":
        names.sort(key=lambda n: (_mtime_key(n), n.lower()))
    elif sort_by == "mtime_desc":
        names.sort(key=lambda n: (-_mtime_key(n), n.lower()))
    else:
        names.sort()
    return names


def get_network_path_for_partition(
    partition_folder_name: str, partitions_path: str | None = None
) -> str:
    """Ruta .../Partitions/<partition_folder_name>/Network."""
    base = partitions_path or get_ultra_partitions_path()
    return os.path.join(base, partition_folder_name, NETWORK_FOLDER_NAME)


def list_network_directory_entries(network_path: str) -> list[tuple[str, str]]:
    """
    Lista entradas dentro de una carpeta Network.

    Returns:
        Lista de (nombre, tipo) con tipo 'dir' o 'file'. Lista vacía si no existe o error.
    """
    if not os.path.isdir(network_path):
        return []

    out: list[tuple[str, str]] = []
    try:
        for name in os.listdir(network_path):
            full = os.path.join(network_path, name)
            kind = "dir" if os.path.isdir(full) else "file"
            out.append((name, kind))
    except OSError:
        return []

    out.sort(key=lambda x: (x[1], x[0].lower()))
    return out


def print_all_network_folders_contents(partitions_path: str | None = None) -> int:
    """
    Por cada subcarpeta de Partitions, entra en Network y muestra su contenido por consola.

    Returns:
        0 si la ruta Partitions existe y se pudo recorrer; -1 si no existe o no es accesible.
    """
    base = partitions_path or get_ultra_partitions_path()

    print()
    print("=" * 60)
    print("Contenido de Network por particion")
    print("=" * 60)
    print(f"Partitions: {base}")
    print()

    if not os.path.isdir(base):
        print(f"No existe o no es accesible: {base}")
        print("=" * 60)
        return -1

    partition_names = get_partition_subfolder_names(base)

    if not partition_names:
        print("(No hay subcarpetas en Partitions para recorrer.)")
        print("=" * 60)
        return 0

    for idx, partition_name in enumerate(partition_names, start=1):
        network_path = get_network_path_for_partition(partition_name, partitions_path=base)
        print("-" * 60)
        print(f"[{idx}/{len(partition_names)}] Particion: {partition_name}")
        print(f"    Network: {network_path}")

        if not os.path.isdir(network_path):
            print(f"    (!) No existe la carpeta Network o no es accesible.")
            print()
            continue

        entries = list_network_directory_entries(network_path)
        if not entries:
            print("    (Carpeta Network vacia o sin listar.)")
            print()
            continue

        print(f"    Contenido ({len(entries)} entradas):")
        for name, kind in entries:
            tag = "[DIR] " if kind == "dir" else "[FILE]"
            print(f"      {tag} {name}")
        print()

    print("=" * 60)
    return 0


def count_partition_folders(partitions_path: str | None = None) -> int:
    """Cantidad de subcarpetas dentro de Partitions."""
    return len(get_partition_subfolder_names(partitions_path))


def sync_ultra_partitions_network_cookies(partitions_path: str | None = None) -> int:
    """
    Por cada carpeta bajo Partitions (orden por creación: mtime ascendente), empareja con cada
    fila de la tabla cookies de la BD (orden por id) y reemplaza el archivo Chromium ``Cookies`` dentro de
    ``.../Network/`` por uno generado con cookie_converter a partir del campo ``cookie``.

    Usa como base el archivo **Cookies** que ya existe en cada ``Network`` (Ultra lo crea al usar
    la pestaña); se vacía la tabla interna y se insertan las cookies del JSON de la BD.

    Returns:
        0 si terminó; -1 si error previo (sin particiones o sin BD).
    """
    from app.helpers.cookie_converter import (
        OUTPUT_NAME,
        fetch_cookie_records_from_app_db,
        parse_record_to_cookie_list,
        write_chrome_cookies_sqlite,
    )

    base = partitions_path or get_ultra_partitions_path()
    if not os.path.isdir(base):
        print(f"[ERROR] No existe la carpeta Partitions: {base}")
        return -1

    partition_names = get_partition_subfolder_names(base, sort_by="mtime_asc")
    records = fetch_cookie_records_from_app_db()

    if not partition_names:
        print("[ERROR] No hay subcarpetas en Partitions.")
        return -1
    if not records:
        print("[ERROR] No hay filas en la tabla cookies (app/database/cookies.db).")
        return -1

    n_part = len(partition_names)
    n_rec = len(records)
    if n_part != n_rec:
        print(
            f"[AVISO] Particiones ({n_part}) y filas en BD ({n_rec}) no coinciden. "
            f"Se procesan solo las primeras {min(n_part, n_rec)} parejas (1:1 por orden)."
        )
    n = min(n_part, n_rec)

    print()
    print("=" * 60)
    print("Sincronizar archivo Cookies en cada .../Network/ (desde BD)")
    print("=" * 60)
    print("Si ya hay Cookies en Network, se sustituye; si no, se crea desde app/helpers/Cookies.")
    print(f"Partitions: {base}")
    print(
        f"Parejas 1:1:      {n} (particion[i] orden creación <-> fila BD ORDER BY id [i])"
    )
    print("=" * 60)
    print()

    for i in range(n):
        pname = partition_names[i]
        rec = records[i]
        network_path = get_network_path_for_partition(pname, partitions_path=base)
        dest = os.path.join(network_path, OUTPUT_NAME)

        cookie_list = parse_record_to_cookie_list(rec)
        if not cookie_list:
            print(
                f"[{i + 1}/{n}] OMITIR  {pname}  (cookie vacia o JSON invalido, id={rec.get('id')})"
            )
            continue

        if not os.path.isdir(network_path):
            print(f"[{i + 1}/{n}] OMITIR  {pname}  (no existe Network: {network_path})")
            continue

        try:
            stats = write_chrome_cookies_sqlite(dest, cookie_list)
            email = (rec.get("email") or "").strip() or "—"
            short = pname[:10] + "..." if len(pname) > 10 else pname
            print(
                f"[{i + 1}/{n}] OK  {short}  |  {email}  |  "
                f"ins={stats['inserted']} dup={stats['skipped']} err={stats['errors']} filas_sqlite={stats['total']}"
            )
        except Exception as e:
            print(f"[{i + 1}/{n}] ERROR {pname}: {e}")

    print()
    print("=" * 60)
    return 0


def main() -> None:
    """Ejecutar: python -m app.ultrabot.cookie_convert [--sync]"""
    parser = argparse.ArgumentParser(
        description="Inspeccionar Partitions/Network o sincronizar archivo Cookies desde la BD."
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Generar y reemplazar el archivo Cookies en cada carpeta Network usando la tabla cookies.",
    )
    args = parser.parse_args()

    if args.sync:
        code = sync_ultra_partitions_network_cookies()
        sys.exit(0 if code >= 0 else 1)

    code = print_all_network_folders_contents()
    sys.exit(0 if code >= 0 else 1)


if __name__ == "__main__":
    main()
