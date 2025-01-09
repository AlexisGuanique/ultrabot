import re

def read_cookies_from_txt(file_path):
    """Lee las cookies desde un archivo de texto y separa bloques delimitados por [ ]."""
    cookies = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()

            # Usar regex para capturar todo bloque que empieza con [ y termina con ]
            cookie_blocks = re.findall(r'\[.*?\]', content, re.DOTALL)

            for block in cookie_blocks:
                # Guardar el bloque completo como una cookie
                cookies.append(block.strip())  # Eliminar espacios en blanco alrededor

        print(f"{len(cookies)} cookies procesadas correctamente.")
        return cookies

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []
