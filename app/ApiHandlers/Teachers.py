from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import JWRefreshTokens
from app.Database import Teachers


# Получение информации об учителе (о себе)
class TeachersApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        if status[0]:
            # Получаем email из токена доступа к сайту и по email-у получаем информацию об учителе
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            access_level = Teachers.get_access_level(email)
            name = Teachers.get_teacher(email)

            return {
                'result': 'OK',
                'access_level': access_level,
                'name': name
            }
        else:
            print('error with token!')
            print(args['access_token'])
            print(status[1])
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
