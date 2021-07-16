from app.ApiHandlers import verification
from flask_restful import Api, Resource, reqparse
from flask import make_response


# Выход из сайта
class Logout(Resource):
    def get(self):
        # Просто куки, отвечающие за токены доступа очищаем)
        resp = make_response({'result': 'OK'})
        resp.set_cookie('access_token', "q")
        resp.set_cookie('refresh_token', "q")

        return resp


# Вход в систему
class Login(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('google_token', type=str)

        args = parser.parse_args()

        # С помощью гугла проверяем, хороший ли токен гугла
        # Эта же функция в случае успеха создает нам токены доступа к нашему сайту
        result = verification.login(args['google_token'])

        # Если токен пустой, значит что-то не так(
        if len(result[0]) == 0:
            return {
                'result': 'Error!',
                'error_message': 'Login failed!'
            }
        else:
            # Если все ок пишем токены в куки пользователя
            resp = make_response({'result': 'OK'})
            resp.set_cookie('access_token', result[1])
            resp.set_cookie('refresh_token', result[0])

            return resp
