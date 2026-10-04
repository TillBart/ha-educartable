"""Constantes de l'intégration Educartable."""
from datetime import timedelta

DOMAIN = "educartable"

AUTH_URL = "https://accounts.edumoov.com/auth/realms/edumoov/protocol/openid-connect/token"
API_URL = "https://app.educartable.com/api/1.0"
CLIENT_ID = "educlasse"

SCAN_INTERVAL = timedelta(minutes=30)
MAX_ITEMS = 10
