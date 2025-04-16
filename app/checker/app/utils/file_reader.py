def read_cookies_from_txt(file_path):
    cookies = []
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()

        for line in content:
            line = line.strip()
            if line:
                cookies.append({"cookie": line})

        return cookies

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []
