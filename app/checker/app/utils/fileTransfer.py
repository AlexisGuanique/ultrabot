import json
import argparse

def extract_and_write_cookies(input_path, output_path):
    cookies = []

    try:
        with open(input_path, 'r') as file:
            content = file.readlines()

        for line in content:
            try:
                email, password, cookie_block = line.split("\t", 2)
                cookie_block = cookie_block.strip().strip('[]')

                cookie_list = json.loads(f'[{cookie_block}]')

                filtered = [
                    {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", True),
                        "httpOnly": cookie.get("httpOnly", False)
                    }
                    for cookie in cookie_list if cookie.get("name") in ["bcookie", "bscookie", "li_at"]
                ]

                cookies.append({
                    "email": email.strip(),
                    "password": password.strip(),
                    "cookies": filtered
                })

            except ValueError:
                print(f"Línea inválida encontrada y omitida: {line.strip()}")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON en la línea: {line.strip()} - {e}")

        with open(output_path, 'w', encoding='utf-8') as output_file:
            for entry in cookies:
                output_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"Cookies escritas correctamente en {output_path}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer cookies útiles y escribirlas en un .txt")
    parser.add_argument("input", help="Ruta al archivo .txt de entrada con las cookies")
    parser.add_argument("output", help="Ruta al archivo .txt de salida donde se guardarán las cookies filtradas")

    args = parser.parse_args()
    extract_and_write_cookies(args.input, args.output)
