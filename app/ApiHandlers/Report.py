import datetime
import json
from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students, Teachers, Subjects, Tasks, Marks, JWRefreshTokens
from config import Metadata
from hashlib import sha256
import base64


def gen_key(filename):
    filename_code = base64.b64encode(filename)
    sumstring = filename + Metadata.SECRET_KEY
    hash = sha256(sumstring)
    key = filename_code + "." + hash
    return key


def check_key(key):
    filename_code, hash = key.split('.')
    filename = base64.b64decode(filename_code)
    sumstring = filename + Metadata.SECRET_KEY
    hash_check = sha256(sumstring)
    if hash_check == hash:
        return filename
    else:
        return False

class ReportApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('date_from', type=str, required=True, help="Date from is not given")
        parser.add_argument('date_to', type=str, required=True, help="Date to is not given")
        parser.add_argument('student_id', type=int, required=True, help="Student id is not given")
        parser.add_argument('comment', type=str)
        parser.add_argument('only_summative', type=bool, required=True, help="Only summative is not given")
        parser.add_argument('subjects_list', type=str, required=True, help="Subjects list is not given")

        try:
            args = parser.parse_args()
        except TypeError as e:
            return {
                "result": "Error!",
                "error_message": str(e)
            }

        if args['comment'] is None:
            args['comment'] = ""

        status = check_access_token(args['access_token'])

        try:
            subjects_list = json.loads(args['subjects_list'])
        except:
            return {
                'result': 'Error!',
                'error_message': 'subjects_list cannot be converted to list'
            }

        try:
            date_from = datetime.datetime.strptime(args['date_from'], '%d.%m.%Y')
            date_to = datetime.datetime.strptime(args['date_to'], '%d.%m.%Y')
        except:
            return {
                'result': 'Error!',
                'error_message': 'Date should be in format %d.%m.%Y'
            }

        if status[0]:
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            creator = Teachers.get_teacher(email)

            # такие поля: student['name'], student['id'], student['grade']
            student = Students.get_student(args['student_id'])
            filename = "report_by_" + creator.replace(' ', '_') + "-" + student['name'].replace(' ', '_') + ".pdf"
            key = gen_key(filename)

            date_today = datetime.datetime.now()

            show_only_summative = args['only_summative']

            # TODO: создать и сформировать файл с отчетом
            # TODO: тут пока просто записать заголовок. Оценки и таблицы будут дальше

            for subject in subjects_list:
                subject_obj = Subjects.get_subject(subject)

                if subject_obj is None:
                    continue

                # такие поля: teacher['email'], teacher['access_level'], teacher['name']
                # teachers - это список учителей
                teachers = Subjects.get_subjects_teachers(subject)

                # такие поля: mark['student_id'], mark['task_id'], mark['mark'] (это значение), mark['max_mark'],
                # mark['criteria'], mark['type'] (summative/formative), mark['timestamp'] (YYYY-MM-DD),
                # mark['description'] (описание задания)
                # marks - это список из оценок
                marks = Marks.get_marks(args['time_from'], args['time_to'], student['id'], subject)

                if len(marks) == 0:
                    continue

                # TODO: заполнить таблицу с текущим предметом

            return {
                'result': 'OK',
                'key': key
            }
        else:
            print('error with token!')
            print(args['access_token'])
            print(status[1])
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
