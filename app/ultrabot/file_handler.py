
def read_cookies_from_txt(file_path):
    cookies = []
    
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()

        for line in content:
            try:
                user_agent, email, password, cookie_block = line.split("\t", 3)
                
                cookie_block = cookie_block.strip()

                cookies.append({
                    "user_agent": user_agent.strip(),
                    "email": email.strip(),
                    "password": password.strip(),
                    "cookie": cookie_block
                })

            except ValueError:
                print(f"Línea inválida encontrada y omitida: {line.strip()}")
            except Exception as e:
                print(f"Error procesando la línea: {line.strip()} - {e}")

        return cookies

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

