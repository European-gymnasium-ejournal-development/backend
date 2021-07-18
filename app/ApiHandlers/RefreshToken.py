from flask_restful import Api, Resource, reqparse
from app.Database import JWRefreshTokens
from create.config import Metadata
from app.ApiHandlers import JWTVerification


# API обновления токена доступа к сайту
class RefreshToken(Resource):
    def get(self):
        # Читаем refresh_token из куки
        parser = reqparse.RequestParser()
        parser.add_argument('refresh_token', location='cookies', type=str)

        args = parser.parse_args()

        if not args['refresh_token']:
            return {
                'result': 'Error!',
                'error_message': 'No refresh token provided'
            }

        # Проверяем, что токен нормальный
        check_result = JWTVerification.check_access_token(args['refresh_token'])

        if not check_result[0]:
            return {
                'result': 'Error!',
                'error_message': check_result[1]
            }

        # Проверяем, что этот токен записан в БД (что он валидный)
        result = JWRefreshTokens.get_token(args['refresh_token'])
        # Достаем из токена email
        email = JWRefreshTokens.parse_email_from_token(args['refresh_token'])

        if result:
            # Возвращаем новый токен и пишем его в куки
            return {
                'result': 'OK'
            }, 200, {
                'Set-Cookie': 'access_token=' +
                              JWRefreshTokens.generate_token(email, Metadata.JSON_WEB_ACCESS_TOKEN_LIFETIME)
            }
        else:
            return {
                'result': 'Error!',
                'error_message': 'Wrong refresh token!'
            }
