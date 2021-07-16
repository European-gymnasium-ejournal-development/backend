import codecs
import datetime
import json
import math
import os
from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students, Teachers, Subjects, Tasks, Marks, JWRefreshTokens
from config import Metadata
from hashlib import sha256
import base64
from fpdf import FPDF
from functools import partial


TITLE_FONT = "DejaVu", 14
SMALL_TEXT_FONT = "DejaVu", 10
TABLE_TEXT_FONT = "DejaVu", 12
MAIN_TEXT_FONT = "DejaVu", 12


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


def date_year_to_date_month(date):
    month, day = date.split('-')[1:]
    date_str = '.'.join([day, month])
    return date_str


def generate_table(marks):
    print(marks)

    dates = set()
    for mark in marks:
        dates.add(mark['timestamp'])

    dates = list(dates)
    dates.sort()

    header = [['Критерий\\Дата']]
    for date in dates:
        header.append([date_year_to_date_month(date)])

    criterias = ['A', 'B', 'C', 'D', '0']
    table = [header]

    for criteria in criterias:
        line = [[criteria if criteria != '0' else 'Без критерия']]
        for time in header[1:]:
            markslist = []
            for mark in marks:
                print(time, date_year_to_date_month(mark['timestamp']))
                if mark['criteria'] == criteria and date_year_to_date_month(mark['timestamp']) == time[0]:
                    markslist.append(mark)

            line.append(markslist)
        table.append(line)

    return table


def draw_table(pdf, table, hat_drawer):
    partsCount = math.ceil((len(table[0]) - 1) / Metadata.REPORT_TABLE_WIDTH)
    index = 1
    pdf.set_font(TABLE_TEXT_FONT[0], size=TABLE_TEXT_FONT[1])

    for part_index in range(0, partsCount):
        index = 1 + part_index * Metadata.REPORT_TABLE_WIDTH
        if part_index % Metadata.TABLES_PER_PAGE == 0 and part_index > 0:
            pdf.add_page()
            hat_drawer()
        else:
            pdf.ln(20)

        pdf.set_draw_color(0, 96, 160)

        pdf.set_font(TABLE_TEXT_FONT[0], size=TABLE_TEXT_FONT[1])

        table_part = [
            [line[0]] + line[index: min(len(table[0]), index + Metadata.REPORT_TABLE_WIDTH)] for line in table
        ]

        table_width = int(pdf.w * 0.9)
        col_width = table_width // (Metadata.REPORT_TABLE_WIDTH + 3)

        table_height = 0

        row_height = int(pdf.font_size * 1.5)

        for line in table_part:
            line_height = row_height * max([len(x) for x in line])
            table_height += line_height

        for line_index, line in enumerate(table_part):
            line_height = row_height * max([len(x) for x in line])

            if line_index != len(table_part) - 1:
                pdf.line(pdf.get_x(), pdf.get_y() + line_height, pdf.get_x() + table_width, pdf.get_y() + line_height)

            for cell_index, cell in enumerate(line):
                if cell_index == 0:
                    width = col_width * 3
                else:
                    width = col_width

                if line_index == 0 and cell_index != len(line) - 1:
                    pdf.line(pdf.get_x() + width, pdf.get_y(), pdf.get_x() + width, pdf.get_y() + table_height)

                if line_index == 0:
                    pdf.cell(width, line_height, txt=cell[0], border=0, align='C')

                else:
                    for index, mark in enumerate(cell):
                        if cell_index > 0:
                            if mark['mark'] == 'N/A':
                                text = mark['mark']
                            else:
                                text = mark['mark'] + "/" + mark['max_mark']
                            if mark['type'] == 'summative':
                                pdf.set_text_color(150, 0, 0)
                            else:
                                pdf.set_text_color(0, 0, 0)
                        else:
                            text = mark
                            pdf.set_text_color(0, 0, 0)

                        ln = 2
                        if index == len(cell) - 1:
                            ln = 0

                        print(text, ln)
                        pdf.cell(width, row_height, txt=text, border=0, ln=ln, align='C')
                    if len(cell) == 0:
                        pdf.cell(width, row_height, txt="", border=0, ln=0)
                    else:
                        pdf.set_xy(pdf.get_x(), pdf.get_y() - ((len(cell) - 1) * row_height))

            pdf.ln(line_height)


def page_hat(pdf, student, date_from, date_to, creator, subject):
    pdf.set_font(SMALL_TEXT_FONT[0], size=SMALL_TEXT_FONT[1])
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())
    text = student['name'] + " | " + student['grade_name'] + " | " + date_from.strftime("%d.%m.%Y") + " - " \
           + date_to.strftime("%d.%m.%Y") + " | " + creator + " | " + subject['name']
    pdf.cell(pdf.w - pdf.get_x() * 2, pdf.font_size * 2, txt=text, align='C', ln=1)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())
    pdf.ln(pdf.font_size * 2)


def title(pdf, subject):
    pdf.set_font(TITLE_FONT[0], size=TITLE_FONT[1])
    pdf.cell(pdf.w - 2 * pdf.get_x(), pdf.font_size * 2, txt=subject['name'], align='C', ln=0)


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

            # такие поля: student['name'], student['id'], student['grade_name']
            student = Students.get_student(args['student_id'])

            my_subjects = [subject['id'] for subject in Subjects.get_student_subjects(student['id'])]

            filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_" + student['name'].replace(' ', '_') + "_by_" \
                       + creator_name.replace(" ", "_") + ".pdf"

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

                pdf.add_page()
                title(pdf, subject_obj)

                table = generate_table(marks)

                draw_table(pdf, table, partial(page_hat, pdf, student, date_from, date_to, creator_name, subject_obj))

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
