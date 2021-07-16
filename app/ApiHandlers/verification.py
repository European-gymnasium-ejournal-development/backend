from google.oauth2 import id_token
from google.auth.transport import requests
from config import Metadata
from app.Database import Teachers
from app.Database import JWRefreshTokens


# Гугловская проверка доступа учителя

def check_email(email):
    return Teachers.get_access_level(email) > 0


# Проверяем с помощью гугла хороший ли гугл-токен нам дали
# Возвращает ok: boolean, email: string
def parse_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), Metadata.GOOGLE_CLIENT_ID)

        print(id_info)
        print(str(id_info))
        return (id_info['email_verified'] and check_email(id_info['email'])), id_info['email']
    except ValueError as e:
        print(e)
        return False, ''


# Попытка залогиниться. Если успешно, то возвращает токены доступа к сайту
# Иначе возвращает две пустые строки
def login(google_token):
    parsed = parse_token(google_token)
    print(parsed)
    if parsed[0]:
        return JWRefreshTokens.update_refresh_token(parsed[1])
    else:
        return '', ''
