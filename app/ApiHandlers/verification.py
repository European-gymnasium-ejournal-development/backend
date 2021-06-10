from google.oauth2 import id_token
from google.auth.transport import requests
from config import Metadata


# TODO: check if such email is in database
def check_email(email):
    return True


def parse_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), Metadata.GOOGLE_CLIENT_ID)
        return id_info['email_verified'] == 'true' and check_email(id_info['email'])
    except ValueError:
        return False
