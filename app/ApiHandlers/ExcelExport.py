import datetime
import os

import xlsxwriter
from copy import deepcopy
from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.ApiHandlers.Report import check_key, gen_key
from app.Database import Students, Marks


# Создание таблицы Summative
def table_sum(workbook, marks):
    table_with_filter(workbook, marks, lambda x: x['type'] == 'summative', 'Summative')


# Создание таблицы Formative
def table_form(workbook, marks):
    table_with_filter(workbook, marks, lambda x: x['type'] == 'formative', 'Formative')


# Создание таблицы Mixed
def table_mix(workbook, marks):
    table_with_filter(workbook, marks, lambda x: True, 'Mixed')


def table_with_filter(workbook, marks, filter, table_name):
    worksheet = workbook.add_worksheet(table_name)
    # Создаю лист с таблицей

    line_index = {'A': {'page': 1, 'line': 0}, 'B': {'page': 1, 'line': 1}, 'C': {'page': 1, 'line': 2},
                  'D': {'page': 1, 'line': 3}, '0': {'page': 1, 'line': 4}}

    cell_index = 1
    # Параметры для записи оценок

    worksheet.write(line_index['A']['line'], 0, "A")
    worksheet.write(line_index['B']['line'], 0, "B")
    worksheet.write(line_index['C']['line'], 0, "C")
    worksheet.write(line_index['D']['line'], 0, "D")
    worksheet.write(line_index['0']['line'], 0, "No criteria")
    # Рисую критерии

    for mark in marks:
        if filter(mark):
            for criteria in mark['mark'].keys():
                # Проверяю тип оценки
                try:
                    worksheet.write_number(line_index[criteria]['line'], cell_index, int(mark['mark'][criteria]))
                except:
                    worksheet.write(line_index[criteria]['line'], cell_index, mark['mark'][criteria])
                # Записываю оценку

            cell_index += 1
            # line_index[mark['criteria']]['page'] += 1
            # Меняю ячейку для следующей записи


def generate_excel(marks, filename):
    marks_dict = {}
    for mark in marks:
        if mark['max_mark'] != '8':
            continue

        key = mark['timestamp'] + ":" + str(mark['student_id']) + ":" + str(mark['task_id'])
        if key in marks_dict.keys():
            marks_dict[key]['mark'][mark['criteria']] = mark['mark']
        else:
            mark_edited = deepcopy(mark)
            mark_edited['mark'] = {mark['criteria']: mark['mark']}
            marks_dict[key] = mark_edited

    marks_list = []
    for key in marks_dict.keys():
        marks_list.append(marks_dict[key])

    path = os.path.join("reports", filename)
    if os.path.exists(path):
        os.remove(path)
    workbook = xlsxwriter.Workbook(path)
    # Создаю файл xlsx

    table_sum(workbook, marks_list)
    table_form(workbook, marks_list)
    table_mix(workbook, marks_list)
    workbook.close()
    

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
        except Exception as e:
            # Если что-то не так, то возвращаем ошибку
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
                # print(args['date_from'], args['date_to'], student['id'], args['subject'])
                all_marks += Marks.get_marks(args['date_from'], args['date_to'], student['id'], args['subject'])

            # print(all_marks)
            all_marks.sort(key=lambda x: x['timestamp'])
            filename = datetime.datetime.now().strftime("%Y-%d-%m") + "-" + args['subject'] + '-' \
                       + args['grade'] + ".xlsx"

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
