from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Teachers, JWRefreshTokens


class AdminApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('new_update_time', type=int)

        args = parser.parse_args()
        new_update_time = args['new_update_time']
        status = check_access_token(args['access_token'])

        if status[0]:
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            access_level = Teachers.get_access_level(email)

            if access_level >= Teachers.AccessLevel.ADMIN:
                # TODO: перезапустить файл с обновлением данных в БД с новыми параметрами
                pass

        else:
            print('error with token!')
            print(args['access_token'])
            print(status[1])
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
