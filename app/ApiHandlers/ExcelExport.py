import datetime
import xlsxwriter

from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.ApiHandlers.Report import check_key, gen_key
from app.Database import Students, Marks


def generate_excel(marks, filename):
    
    workbook = xlsxwriter.Workbook(filename + ".xlsx")
    #Создаю файл xlsx
    
    #Создание таблицы Summative
    def table_sum(marks):
        worksheet_sum = workbook.add_worksheet('Summative')
        #Создаю лист с таблицей

        line_index = {'A': {'page' : 1, 'line' : 0}, 'B': {'page' : 1, 'line' : 1}, 'C': {'page' : 1, 'line' : 2}, 'D': {'page' : 1, 'line' : 3}, '0': {'page' : 1, 'line' : 4}}
        #Параметры для записи оценок

        worksheet_sum.write(line_index['A']['line'],0,"A")
        worksheet_sum.write(line_index['B']['line'],0,"B")
        worksheet_sum.write(line_index['C']['line'],0,"C")
        worksheet_sum.write(line_index['D']['line'],0,"D")
        worksheet_sum.write(line_index['0']['line'],0,"None")
        #Рисую критерии

        for mark in marks:

            if mark['type'] == 'summative':
            #Проверяю тип оценки
                
                worksheet_sum.write_number(line_index[mark['criteria']]['line'],line_index[mark['criteria']]['page'],int(mark['mark']))
                #Записываю оценку

                line_index[mark['criteria']]['page'] += 1
                #Меняю ячейку для следующей записи


    #Создание таблицы Formative
    def table_form(marks):
        worksheet_form = workbook.add_worksheet('Formative')
        #Создаю лист с таблицей

        line_index = {'A': {'page' : 1, 'line' : 0}, 'B': {'page' : 1, 'line' : 1}, 'C': {'page' : 1, 'line' : 2}, 'D': {'page' : 1, 'line' : 3}, '0': {'page' : 1, 'line' : 4}}
        #Параметры для записи оценок


        worksheet_form.write(line_index['A']['line'],0,"A")
        worksheet_form.write(line_index['B']['line'],0,"B")
        worksheet_form.write(line_index['C']['line'],0,"C")
        worksheet_form.write(line_index['D']['line'],0,"D")
        worksheet_form.write(line_index['0']['line'],0,"None")
        #Рисую критерии

        for mark in marks:

            if mark['type'] == 'formative':
            #Проверяю тип оценки
                worksheet_form.write_number(line_index[mark['criteria']]['line'],line_index[mark['criteria']]['page'],int(mark['mark']))
                #Записываю оценку

                line_index[mark['criteria']]['page'] += 1
                #Меняю ячейку для следующей записи

    #Создание таблицы Mixed
    def table_mix(marks):
        worksheet_mix = workbook.add_worksheet('Mixed')
        #Создаю лист с таблицей

        line_index = {'A': {'page' : 1, 'line' : 0}, 'B': {'page' : 1, 'line' : 1}, 'C': {'page' : 1, 'line' : 2}, 'D': {'page' : 1, 'line' : 3}, '0': {'page' : 1, 'line' : 4}}
        #Параметры для записи оценок


        worksheet_mix.write(line_index['A']['line'],0,"A")
        worksheet_mix.write(line_index['B']['line'],0,"B")
        worksheet_mix.write(line_index['C']['line'],0,"C")
        worksheet_mix.write(line_index['D']['line'],0,"D")
        worksheet_mix.write(line_index['0']['line'],0,"None")
        #Рисую критерии

        for mark in marks:
            worksheet_mix.write_number(line_index[mark['criteria']]['line'],line_index[mark['criteria']]['page'],int(mark['mark']))
            #Записываю оценку

            line_index[mark['criteria']]['page'] += 1
            #Меняю ячейку для следующей записи


    
    table_sum(marks)
    table_form(marks)
    table_mix(marks)
    workbook.close()
    


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
