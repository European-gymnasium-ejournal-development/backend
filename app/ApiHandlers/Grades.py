from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students


# Получение всех классов, которые есть в системе
class GradesApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])
        # Если у пользователя есть доступ
        if status[0]:
            # Получаем из БД и возвращаем
            grades_list = Students.get_all_grades()
            # Структура - list of string
            return {
                'result': 'OK',
                'grades': grades_list
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
