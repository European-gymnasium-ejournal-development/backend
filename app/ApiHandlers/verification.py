from google.oauth2 import id_token
from google.auth.transport import requests
from config import Metadata
from app.Database import Teachers
from app.ApiHandlers import JWTVerification


def check_email(email):
    return Teachers.get_access_level(email) > 0


def parse_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), Metadata.GOOGLE_CLIENT_ID)
        return (id_info['email_verified'] and check_email(id_info['email'])), id_info['email']
    except ValueError:
        return False, ''


def login(google_token):
    parsed = parse_token(google_token)
    if parsed[0]:
        return JWTVerification.update_refresh_token(parsed[1])
    else:
        return '', ''
