"""
Configuración centralizada del servidor para el bot.

Edita SOLO `SERVER_BASE_URL` para cambiar entre dev/prod.
"""

from __future__ import annotations

# CAMBIA ESTE VALOR CUANDO QUIERAS APUNTAR A OTRO AMBIENTE.
# Ejemplo dev: "http://127.0.0.1:5000"
SERVER_BASE_URL = "http://127.0.0.1:5000"

SERVER_BASE_URL = SERVER_BASE_URL.rstrip("/")
AUTH_BASE_API_URL = f"{SERVER_BASE_URL}/api/auth"
LOGIN_URL = f"{AUTH_BASE_API_URL}/login"
VERIFY_TOKEN_URL = f"{AUTH_BASE_API_URL}/verify-token"
ACCOUNTS_NEXT_URL_TEMPLATE = f"{SERVER_BASE_URL}/api/accounts/next/{{user_id}}"
ACCOUNTS_COUNT_URL_TEMPLATE = f"{SERVER_BASE_URL}/api/accounts/count/{{user_id}}"
WEBSOCKET_URL = SERVER_BASE_URL
