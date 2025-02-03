# Gestor de Cookies

El **Gestor de Cookies** es una aplicación que permite leer cookies almacenadas en un archivo `.txt`, separarlas en bloques delimitados por corchetes `[]`, y almacenarlas como registros únicos en una base de datos SQLite. La aplicación también proporciona una interfaz gráfica para facilitar la selección del archivo y gestionar las cookies.

## Características

- **Lectura de Cookies**: Procesa archivos `.txt` que contienen bloques de cookies en formato JSON.
- **Separación por Bloques**: Cada bloque delimitado por `[` y `]` es tratado como una cookie única.
- **Almacenamiento**: Guarda cada cookie como un registro de texto en una base de datos SQLite.
- **Interfaz Gráfica**: Permite seleccionar archivos y visualizar cookies almacenadas mediante una GUI construida con Tkinter.

## Requisitos

- Python 3.7 o superior
- Bibliotecas adicionales:
  - `sqlite3` (incluida por defecto con Python)
  - `tkinter` (incluido por defecto con Python)

## Instalación

1. Clona este repositorio o descarga el código fuente:
   ```bash
   git clone https://github.com/tuusuario/gestor-de-cookies.git
   cd gestor-de-cookies
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar la Aplicación

1. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```

2. Selecciona un archivo `.txt` que contenga cookies en formato JSON usando la interfaz gráfica.
3. Procesa y almacena las cookies en la base de datos SQLite.
4. Usa la opción de "Mostrar Cookies" para visualizar las cookies almacenadas.

### Formato del Archivo de Entrada
El archivo `.txt` debe contener bloques de cookies en el siguiente formato:

```json
[ { "name": "cookie1", "value": "abc123" }, { "name": "cookie2", "value": "def456" } ]
[ { "name": "cookie3", "value": "ghi789" } ]
```

Cada bloque delimitado por `[` y `]` se considera una cookie independiente.

## Arquitectura del Proyecto

```
mi_proyecto/
│
├── main.py              # Punto de entrada de la aplicación
├── database.py          # Gestión de la base de datos
├── file_handler.py      # Lectura y procesamiento de archivos .txt
├── ui.py                # Interfaz gráfica con Tkinter
├── cookies.db           # Base de datos SQLite (generada automáticamente)
├── cookies.txt          # Archivo de ejemplo con cookies (opcional)
├── requirements.txt     # Dependencias del proyecto
```

## Funciones Principales

### Lectura de Cookies
- Procesa un archivo `.txt` para extraer bloques de cookies delimitados por `[` y `]`.

### Almacenamiento de Cookies
- Cada bloque de cookies se guarda como un registro único en formato JSON en SQLite.

### Interfaz Gráfica
- Permite seleccionar el archivo a procesar y mostrar las cookies almacenadas.

## Pruebas

1. Crea un archivo `cookies.txt` con el formato adecuado.
2. Ejecuta la aplicación y selecciona el archivo desde la GUI.
3. Verifica que las cookies se almacenen correctamente en la base de datos usando herramientas como [DB Browser for SQLite](https://sqlitebrowser.org/) o comandos SQL:
   ```bash
   sqlite3 cookies.db
   SELECT * FROM cookies;
   ```

## Contribuciones

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad:
   ```bash
   git checkout -b nueva-funcionalidad
   ```
3. Realiza tus cambios y haz commit:
   ```bash
   git commit -m "Agrega nueva funcionalidad"
   ```
4. Envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.

pyinstaller --onefile --windowed --icon="C:\Users\Usuario\workspace\ultra\ultrabot\favicon.ico" --name=UltraBot --add-data="app/database/cookies.db;app/database/" --add-data="app/ultrabot/images;app/ultrabot/images" main.py
