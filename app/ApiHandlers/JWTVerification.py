import base64
from hashlib import sha256
from config import Metadata
import datetime


# Модуль проверки подлинность json web токенов

# Проверяем токен на его правильность и что он не просрочился
# Возвращает True/False, error_message
# True, "", если все ок
# False, problem: string, если что-то пошло не так
def check_access_token(token):
    if not token:
        return False, 'no token!'

    # Токен обязательно должен иметь формат с двумя точками-разделителями
    if len(token.split(".")) != 3:
        return False, 'wrong token format'

    header_b64, payload_b64, signature = token.split('.')

    # Сверяем хеш
    total_string = header_b64 + "." + payload_b64 + "@" + Metadata.SECRET_KEY
    signature_check = sha256(total_string.encode('ascii')).hexdigest()

    if signature_check != signature:
        return False, 'signature'

    # Декодируем данные в заголовке
    header = base64.b64decode(header_b64)
    header = eval(header)
    if header['alg'] != 'HS256' and header['typ'] != 'JWT':
        return False, 'header'

    payload = base64.b64decode(payload_b64)
    payload = eval(payload)

    # Проверяем, что срок действия токена не истек
    now = (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds()

    if payload['exp'] < now:
        return False, 'expired'

    return True, ''
