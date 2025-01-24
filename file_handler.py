def read_cookies_from_txt(file_path):
    """
    Lee las cookies desde un archivo de texto y separa el email, el password y bloques delimitados por [ ].
    """
    cookies = []
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()

        for line in content:
            # Separar email, password y cookie usando tabulación como delimitador
            try:
                email, password, cookie_block = line.split("\t", 2)
                cookies.append({
                    "email": email.strip(),
                    "password": password.strip(),
                    "cookie": cookie_block.strip()
                })
            except ValueError:
                print(f"Línea inválida encontrada y omitida: {line.strip()}")

        print(f"{len(cookies)} cookies procesadas correctamente.")
        return cookies

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []
