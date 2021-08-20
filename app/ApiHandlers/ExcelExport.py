import datetime

from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.ApiHandlers.Report import check_key, gen_key
from app.Database import Students, Marks


def generate_excel(marks, filename):
    pass


# Получение всех классов, которые есть в системе
class ExcelExport(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('date_from', type=str, required=True, help="Date from is not given")
        parser.add_argument('date_to', type=str, required=True, help="Date to is not given")
        parser.add_argument('subject', type=str, required=True, help="Subject is not specified")
        parser.add_argument('grade', type=str, required=True, help="Grade is not specified")

        # Пробуем распарсить запрос
        try:
            args = parser.parse_args()
            print(args)
        except Exception as e:
            # Если что-то не так, то возвращаем ошибку
            print(e)
            return {
                "result": "Error!",
                "error_message": str(e)
            }

        # Пробуем распарсить даты
        try:
            date_from = datetime.datetime.strptime(args['date_from'], '%d.%m.%Y')
            date_to = datetime.datetime.strptime(args['date_to'], '%d.%m.%Y')
        except:
            return {
                'result': 'Error!',
                'error_message': 'Date should be in format %d.%m.%Y'
            }

        status = check_access_token(args['access_token'])

        all_marks = []

        # Если у пользователя есть доступ
        if status[0]:
            students = Students.get_all_students_of_grade(args['grade'])
            for student in students:
                all_marks += Marks.get_marks(date_from, date_to, student['id'], args['subject'])

            all_marks.sort(key=lambda x: x['timestamp'])
            filename = datetime.datetime.now().strftime("%Y-%d-%m") + "-" + args['subject'] + '-' + args['grade']

            generate_excel(all_marks, filename)
            key = gen_key(filename)

            return {
                'result': 'OK',
                'key': key
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
