import base64
from hashlib import sha256
from config import Metadata
import datetime


def check_access_token(token):
    if not token:
        return False, 'no token!'

    header_b64, payload_b64, signature = token.split('.')

    total_string = header_b64 + "." + payload_b64 + "@" + Metadata.SECRET_KEY
    signature_check = sha256(total_string.encode('ascii')).hexdigest()
    if signature_check != signature:
        return False, 'signature'

    header = base64.b64decode(header_b64)
    header = eval(header)
    if header['alg'] != 'HS256' and header['typ'] != 'JWT':
        return False, 'header'

    payload = base64.b64decode(payload_b64)
    payload = eval(payload)

    now = (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds()

    print(payload['exp'] - now)
    print(token)
    if payload['exp'] < now:
        return False, 'expired'

    return True, ''
