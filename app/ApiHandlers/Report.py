import codecs
import datetime
import json
import os

from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students, Teachers, Subjects, Tasks, Marks, JWRefreshTokens
from config import Metadata
from hashlib import sha256
import base64
from fpdf import FPDF


def gen_key(filename):
    filename_code = base64.b64encode(filename.encode('utf-8')).decode('utf-8')


    expiration = datetime.datetime.now() + datetime.timedelta(seconds=10)
    epoch = datetime.datetime(1970, 1, 1)
    timestamp = (expiration - epoch) // datetime.timedelta(microseconds=1)
    print(timestamp)
    expiration_code = str(timestamp)

    sumstring = (filename_code + expiration_code + Metadata.SECRET_KEY).encode('ascii')

    hash = sha256(sumstring).hexdigest()
    key = filename_code + "." + expiration_code + "." + hash
    key = str(key.encode('utf-8').hex())
    return key


def check_key(key):
    key = codecs.decode(key, "hex").decode('utf-8')

    if len(key.split(".")) != 3:
        return False

    filename_code, timestamp, hash = key.split('.')

    filename = base64.b64decode(filename_code).decode('utf-8')

    sumstring = (filename_code + timestamp + Metadata.SECRET_KEY).encode('ascii')

    epoch = datetime.datetime(1970, 1, 1)

    try:
        timestamp = int(timestamp)
    except:
        return False

    if datetime.datetime.now() > (epoch + datetime.timedelta(microseconds=timestamp)):
        print('TIME PROBLEM!!!\n\n\n')
        return False

    hash_check = sha256(sumstring).hexdigest()

    print(hash_check)
    print(hash)
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
        parser.add_argument('only_summative', type=bool, required=True, help="Only summative is not given")
        parser.add_argument('subjects_list', type=str, required=True, help="Subjects list is not given")
        parser.add_argument('student_id', type=int, required=True, help="Student id is not given")
        parser.add_argument('comment', type=str)

        try:
            args = parser.parse_args()
            print(args)
        except Exception as e:
            print(e)
            return {
                "result": "Error!",
                "error_message": str(e)
            }

        if args['comment'] is None:
            args['comment'] = ""
        else:
            args['comment'] = codecs.decode(args['comment'], "hex").decode('utf-8')

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
            creator_name = Teachers.get_teacher(email)

            # такие поля: student['name'], student['id'], student['grade']
            student = Students.get_student(args['student_id'])

            my_subjects = [subject['id'] for subject in Subjects.get_student_subjects(student['id'])]

            filename = "report_by_" + creator_name.replace(' ', '_') + "-" + student['name'].replace(' ', '_') + ".pdf"
            key = gen_key(filename)

            date_today = datetime.datetime.now()

            show_only_summative = args['only_summative']

            pdf = FPDF()
            pdf.add_page()
            # Тут надо использовать русские шрифты
            # https://github.com/reingart/pyfpdf/releases
            pdf.add_font("DejaVu", '', 'fonts\\DejaVuSans.ttf', uni=True)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(w=200, h=10, txt="Отчет о работе", ln=1, align="C")

            prepared_text = "Подготовил(а): " + creator_name + " (" + email + ")"

            pdf.cell(w=200, h=10, txt=prepared_text, ln=1, align="C")

            # TODO: создать и сформировать файл с отчетом
            # TODO: тут пока просто записать заголовок. Оценки и таблицы будут дальше

            for subject in subjects_list:
                if subject not in my_subjects:
                    continue

                # такие поля: teacher['email'], teacher['access_level'], teacher['name']
                # teachers - это список учителей
                teachers = Subjects.get_subjects_teachers(subject)

                # параметры: subject_obj['id'], subject_obj['name']
                subject_obj = Subjects.get_subject(subject)

                if subject_obj is None:
                    continue

                # TODO: заполнить шапку с предметами


            for subject in subjects_list:
                if subject not in my_subjects:
                    continue

                subject_obj = Subjects.get_subject(subject)

                if subject_obj is None:
                    continue

                # такие поля: mark['student_id'], mark['task_id'], mark['mark'] (это значение), mark['max_mark'],
                # mark['criteria'], mark['type'] (summative/formative), mark['timestamp'] (YYYY-MM-DD),
                # mark['description'] (описание задания)
                # marks - это список из оценок
                marks = Marks.get_marks(args['date_from'], args['date_to'], student['id'], subject)

                if len(marks) == 0:
                    continue

                # TODO: заполнить таблицу с текущим предметом

            pdf.output(os.path.join("reports", filename))

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
