from app.Database import db, Integer, String, ForeignKey, Column, DateTime, Tasks, Teachers
import datetime
from create.config import Metadata
from hashlib import sha256
import base64


# БД с refresh-токенами, тут хранятся токены пользователей
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


# Создание токена для email-a, который будет валидным lifetime
def generate_token(email, lifetime):
    # Получаем права учителя, чтобы их записать в токен
    teacher_rights = Teachers.get_access_level(email)

    if teacher_rights == Teachers.AccessLevel.NO_ACCESS:
        return ""

    # Заголовок токена
    header = {"alg": "HS256", "typ": "JWT"}

    # Считаем время, когда выйдет валидность токена
    now = (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds()
    expiration = now + lifetime

    # Тело токена
    payload = {"email": email, "teacher_rights": teacher_rights, "exp": expiration}

    # Кодируем в base64
    header_b64 = base64.b64encode(str(header).encode('utf-8')).decode('utf-8')
    payload_b64 = base64.b64encode(str(payload).encode('utf-8')).decode('utf-8')

    # Создаем hash-подпись токена
    signature = sha256((header_b64 + "." + payload_b64 + "@" + Metadata.SECRET_KEY).encode('ascii')).hexdigest()
    # Склеиваем весь токен в одно
    token = header_b64 + "." + payload_b64 + "." + signature

    return token


# Создаем новый refresh-token и новый access-token
def update_refresh_token(email):
    tokens = (generate_token(email, Metadata.JSON_WEB_REFRESH_TOKEN_LIFETIME),
              generate_token(email, Metadata.JSON_WEB_ACCESS_TOKEN_LIFETIME))

    if len(tokens[0]) == 0:
        return "", ""

    request = JWRefreshToken.query.filter_by(email=email)

    # Записываем refresh-token в БД
    if request.first() is None:
        to_add = JWRefreshToken(email, tokens[0])
        db.session.add(to_add)
    else:
        request.update(dict(token=tokens[0]))

    db.session.commit()
    return tokens


# контракт: токен валидный
def parse_email_from_token(token):
    # Делим токен, вытаскиваем тело
    header_b64, payload_b64, signature = token.split('.')

    # из тела достаем email
    payload = base64.b64decode(payload_b64)
    payload = eval(payload)
    return payload['email']


# Проверяет, есть ли такой токен в БД. Если есть, то возвращает его, иначе None
def get_token(token):
    request = JWRefreshToken.query.filter_by(token=token).first()
    return request is not None


# Удаляет токены всех учителей, которые не обновлены (которые вскоре сами будут удалены)
def delete_not_updated():
    JWRefreshToken.query.filter(
        JWRefreshToken.email.in_(
            Teachers.Teacher.query.filter_by(is_updated=False).with_entities(Teachers.Teacher.email))).delete(
        synchronize_session="fetch")
    db.session.commit()
