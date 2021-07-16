from flask_restful import Api, Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token


# Это вообще тестовый класс) На него можно забить
# Возвращает hello world
class HelloHandler(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])
        if status[0]:
            return {
                'result': 'OK',
                'message': 'Hello world!'
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
