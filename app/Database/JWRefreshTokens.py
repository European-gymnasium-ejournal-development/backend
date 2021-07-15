from app.Database import db, Integer, String, ForeignKey, Column, DateTime, Tasks, Teachers
import datetime
from config import Metadata
from hashlib import sha256
import base64


class JWRefreshToken(db.Model):
    __tablename__ = 'JWRefreshTokens'
    email = Column('teacher_email', ForeignKey('teachers.email'), unique=True, primary_key=True)
    token = Column('token', String(256))

    def __init__(self, email, token):
        self.email = email
        self.token = token

    def to_json(self):
        return {
            'email': self.email,
            'token': self.token
        }


def generate_token(email, lifetime):
    teacher_rights = Teachers.get_access_level(email)

    if teacher_rights == Teachers.AccessLevel.NO_ACCESS:
        return ""

    header = {"alg": "HS256", "typ": "JWT"}

    now = (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds()
    expiration = now + lifetime

    payload = {"email": email, "teacher_rights": teacher_rights, "exp": expiration}

    header_b64 = base64.b64encode(str(header).encode('utf-8')).decode('utf-8')
    payload_b64 = base64.b64encode(str(payload).encode('utf-8')).decode('utf-8')

    signature = sha256((header_b64 + "." + payload_b64 + "@" + Metadata.SECRET_KEY).encode('ascii')).hexdigest()
    token = header_b64 + "." + payload_b64 + "." + signature

    return token


def update_refresh_token(email):
    tokens = (generate_token(email, Metadata.JSON_WEB_REFRESH_TOKEN_LIFETIME),
              generate_token(email, Metadata.JSON_WEB_ACCESS_TOKEN_LIFETIME))

    print("tokens", tokens)

    if len(tokens[0]) == 0:
        return "", ""

    request = JWRefreshToken.query.filter_by(email=email)

    if request.first() is None:
        to_add = JWRefreshToken(email, tokens[0])
        db.session.add(to_add)
    else:
        request.update(dict(token=tokens[0]))

    db.session.commit()
    return tokens


def parse_email_from_token(token):
    header_b64, payload_b64, signature = token.split('.')

    payload = base64.b64decode(payload_b64)
    payload = eval(payload)
    return payload['email']


def get_token(token):
    request = JWRefreshToken.query.filter_by(token=token).first()
    return request is not None
