# file_reader.py

def read_text_from_file(file_path="cookie.txt"):
    """
    Lee y devuelve el contenido del archivo .txt.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()
