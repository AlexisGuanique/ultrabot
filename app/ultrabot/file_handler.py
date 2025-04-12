import json

def read_cookies_from_txt(file_path):
    cookies = []
    
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()

        for line in content:
            try:
                email, password, cookie_block = line.split("\t", 2)
                
                cookie_block = cookie_block.strip().strip('[]')

                cookie_list = json.loads(f'[{cookie_block}]')

                filtered_cookies = [cookie for cookie in cookie_list if cookie.get("name") in ["bcookie", "bscookie", "li_at"]]

                cookies.append({
                    "email": email.strip(),
                    "password": password.strip(),
                    "cookie": json.dumps(filtered_cookies)
                })

            except ValueError:
                print(f"Línea inválida encontrada y omitida: {line.strip()}")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON en la línea: {line.strip()} - {e}")

        return cookies

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []