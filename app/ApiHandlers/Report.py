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


def jshex_to_str(data):
    char_parts = [data[i: i + 4] for i in range(0, len(data), 4)]
    result = ""
    for char in char_parts:
        result += chr(int(char, 16))

    return result


# Модуль создания отчета
TITLE_FONT = "Trebuchet MS", 18
INFO_FONT = "Trebuchet MS", 14
SUBJECT_TITLE_FONT = "Trebuchet MS", 14
SMALL_TEXT_FONT = "Trebuchet MS", 9
TABLE_TEXT_FONT = "Trebuchet MS", 12
MAIN_TEXT_FONT = "Trebuchet MS", 12
STUDENT_INFO_FONT = "Trebuchet MS", 11

SUBJECT_OFFSET = 24

BLUE_COLOR = 0, 96, 160

AFTER_SUBJECT_SPACE = 20
AFTER_TABLE_SPACE = 10
AFTER_TITLE_SPACE = 15
AFTER_HEADER_SPACE = 10


# Создания ключа на скачивание файла с отчетом (название файла - filename)
def gen_key(filename):
    # Сначала кодируем имя в base64
    filename_code = base64.b64encode(filename.encode('utf-8')).decode('utf-8')

    # Задаем срок действия токена +10 сек от сейчас
    expiration = datetime.datetime.now() + datetime.timedelta(seconds=10)
    epoch = datetime.datetime(1970, 1, 1)
    timestamp = (expiration - epoch) // datetime.timedelta(microseconds=1)
    # Переводим время в кол-во миллисекунд
    expiration_code = str(timestamp)

    # Складываем все строки, чтобы собрать хеш
    sumstring = (filename_code + expiration_code + Metadata.SECRET_KEY).encode('ascii')

    # Собираем хеш
    hash = sha256(sumstring).hexdigest()
    # Складываем все вместе в ключ
    key = filename_code + "." + expiration_code + "." + hash
    # Кодируем ключ в hex, чтобы не было всяких плохих символов, которые http неправильно поймет
    key = str(key.encode('utf-8').hex())
    return key


# Проверка подлинности ключа
# Возвращает имя файла или False, если ключ недействителен
def check_key(key):
    # Декодируем ключ из hex
    key = codecs.decode(key, "hex").decode('utf-8')

    # Проверяем, что у ключа нужный формат
    if len(key.split(".")) != 3:
        return False

    # Делим на три части
    filename_code, timestamp, hash = key.split('.')

    # Декодируем имя файла
    filename = base64.b64decode(filename_code).decode('utf-8')

    # Собираем общую строку, чтобы сверить хеши
    sumstring = (filename_code + timestamp + Metadata.SECRET_KEY).encode('ascii')

    epoch = datetime.datetime(1970, 1, 1)

    # Переводим время из строки в datetime
    try:
        timestamp = int(timestamp)
    except:
        return False

    # Если токен уже истек
    if datetime.datetime.now() > (epoch + datetime.timedelta(microseconds=timestamp)):
        return False

    # Сверяем хеши
    hash_check = sha256(sumstring).hexdigest()

    if hash_check == hash:
        return filename
    else:
        return False


# Перевод строки вида YYYY-MM-DD в строку вида DD.MM
def date_year_to_date_month(date):
    month, day = date.split('-')[1:]
    date_str = '.'.join([day, month])
    return date_str


# Создание табличной стркутруы из списка оценок
# Итоговая структура такая:
# [одна строка таблицы: [одна ячейка таблицы: [оценка (json из Database.Marks.Mark)]]]
def generate_table(marks):
    # Соберем все даты
    dates = set()
    for mark in marks:
        dates.add(mark['timestamp'])

    # Превратим их в список и посортируем
    dates = list(dates)
    dates.sort()

    # Соберем заголовок таблицы
    header = [['Criteria\\Date']]
    for date in dates:
        header.append([date_year_to_date_month(date)])

    # Дальше будем для каждого критерия выполнять одинаковый алгоритм
    criterias = ['A', 'B', 'C', 'D', '0']
    table = [header]

    # Сложность алгоритма по времени O(n^2), где n - кол-во оценок, но n обычно маленькое, так что пофиг на сложность
    for criteria in criterias:
        # Добавим заголовок в строку таблицы
        line = [[criteria if criteria != '0' else 'No criteria']]
        # Идем по всем датам, которые когда-либо встречались

        for time in header[1:]:
            # Добавляем в таблицу список всех оценок с нужной датой и нужным критерием
            markslist = []
            for mark in marks:
                if mark['criteria'] == criteria and date_year_to_date_month(mark['timestamp']) == time[0]:
                    markslist.append(mark)

            line.append(markslist)
        table.append(line)

    return table


# Рисование таблицы с одним предметом
# pdf - объект FPDF, на котором все рисуется
# table - массив массивов массивов, полученный из функции generate_table()
# hat_drawer - функция, рисующая шапку к странице
# subject - данные о предмете, таблицу оценок по которому рисуем
def draw_table(pdf, table, hat_drawer, subject):
    # Узнаем, на сколько частей придется бить таблицу
    partsCount = math.ceil((len(table[0]) - 1) / Metadata.REPORT_TABLE_WIDTH)

    pdf.set_font(TABLE_TEXT_FONT[0], size=TABLE_TEXT_FONT[1])
    pdf.set_line_width(0.3)
    # Каждую часть рисуем отдельно
    for part_index in range(0, partsCount):
        # Индекс колонки в таблице, с которого начинается эта часть
        index = 1 + part_index * Metadata.REPORT_TABLE_WIDTH

        # Выделим часть таблицы (не забываем про заголовок (line[0]), который есть у каждой части таблицы)
        table_part = [
            [line[0]] + line[index: min(len(table[0]), index + Metadata.REPORT_TABLE_WIDTH)] for line in table
        ]

        # Считаем размер колонок
        table_width = int(pdf.w * 0.9)
        col_width = table_width // (Metadata.REPORT_TABLE_WIDTH + 1)

        table_height = 0
        # Размер одной строки в таблице (если в строке не больше одной оценки в ячейке)
        row_height = int(pdf.font_size * 1.5)

        # Считаем высоту всей таблицы
        for line in table_part:
            # Находим размер ячейки в таблице
            line_height = row_height * max([len(x) for x in line])
            table_height += line_height

        # Если страница кончилась, то создаем новую и рисуем шапку
        page_height = pdf.h * 0.95

        if part_index > 0:
            delta = AFTER_TABLE_SPACE
            if page_height < delta + table_height + pdf.get_y():
                pdf.add_page()
                hat_drawer()
            else:
                # Иначе просто отсутпаем от прошлой части таблицы
                pdf.ln(AFTER_TABLE_SPACE)
        else:
            delta = AFTER_SUBJECT_SPACE + AFTER_TITLE_SPACE
            # Если начинаем новую страницу, то надо рисовать шапку
            if page_height < pdf.get_y() + delta + table_height:
                pdf.add_page()
                hat_drawer()
            else:
                # Иначе надо отступить от прошлого предмета
                pdf.ln(AFTER_SUBJECT_SPACE)

            # if offset == 0:
            #
            # else:

            # Рисуем заголовок к предмету
            title(pdf, subject)

        # if (part_index + offset) % Metadata.TABLES_PER_PAGE == 0 and part_index > 0:
        #
        # else:

        # Задаем цвета и шрифты
        pdf.set_draw_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(TABLE_TEXT_FONT[0], size=TABLE_TEXT_FONT[1])

        # Рисуем таблицу
        for line_index, line in enumerate(table_part):
            # Считаем высоту ячейки в этой строке
            line_height = row_height * max([len(x) for x in line])

            # Если это не последняя строка, то послее нее надо нарисовать горизонтальный росчерк
            # (границы таблицы рисуются отдельно линиями)
            if line_index != len(table_part) - 1:
                pdf.line(pdf.get_x(), pdf.get_y() + line_height, pdf.get_x() + table_width, pdf.get_y() + line_height)

            # Идем по всем ячейкам
            for cell_index, cell in enumerate(line):
                # Если это первая ячейка (заголовок), то делаем ее шире и выше
                if cell_index == 0:
                    width = col_width * 1
                    height = line_height
                else:
                    # Иначе обычная ширина, а высоту растягиваем так, чтобы все было красиво отцентрированно
                    width = col_width
                    if len(cell) > 0:
                        height = line_height // len(cell)

                # Если это первая строка и не последний столбец, то надо нарисовать вертикальный росчерк
                # на высоту всей таблицы
                if line_index == 0 and cell_index != len(line) - 1:
                    pdf.line(pdf.get_x() + width, pdf.get_y(), pdf.get_x() + width, pdf.get_y() + table_height)

                if cell_index == 0 and len(cell[0]) > 1:
                    pdf.set_font(SMALL_TEXT_FONT[0], size=SMALL_TEXT_FONT[1])
                else:
                    pdf.set_font(TABLE_TEXT_FONT[0], size=TABLE_TEXT_FONT[1])

                # Если это первая строка (заголовок с датами), то просто пишем текст
                if line_index == 0:
                    pdf.cell(width, line_height, txt=cell[0], border=0, align='C')

                else:
                    # Если это строка с оценками, то все сложнее
                    # Итерируемся по оценкам
                    for index, mark in enumerate(cell):
                        # Если это не заголовок (не название критерия)
                        if cell_index > 0:
                            # Выберем, какой текст писать
                            if mark['mark'] == 'N/A':
                                text = mark['mark']
                            else:
                                text = mark['mark'] + "/" + mark['max_mark']

                            # Выбираем цвет текста в зависимости от типа оценки
                            if mark['type'] == 'summative':
                                pdf.set_text_color(150, 0, 0)
                            else:
                                pdf.set_text_color(0, 0, 0)
                        else:
                            # Если же это название критерия, то текст - просто название, а цвет - черный
                            text = mark
                            pdf.set_text_color(0, 0, 0)

                        # Выбираем, какой делать отступ после себя
                        # Если это не последняя оценка в этой ячейке, то после ее написания надо перейти вниз
                        ln = 2
                        # Если же это последняя оценка, то надо после ее написания перейти вправо
                        if index == len(cell) - 1:
                            ln = 0
                        # Рисуем оценку
                        pdf.cell(width, height, txt=text, border=0, ln=ln, align='C')
                    # Если же не нарисовали ни одной оценки, то рисуем пустоту
                    if len(cell) == 0:
                        pdf.cell(width, row_height, txt="", border=0, ln=0)
                    else:
                        # А вот если что-то нарисовали, то надо поднять current на уровень начала строки
                        # На height оно автоматически поднимается при переносе строки с помощью ln = 0
                        # А вот еще на (len(cell) - 1) * height придется поднимать самим
                        pdf.set_xy(pdf.get_x(), pdf.get_y() - ((len(cell) - 1) * height))
            # Делаем отступ на следующую строку
            pdf.ln(line_height)


# Рисование заголовка страницы
def page_hat(pdf, student, date_from, date_to, creator, subject):
    # Выбираем шрифты и тексты
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_font(SMALL_TEXT_FONT[0], size=SMALL_TEXT_FONT[1])
    # Рисуем отчерк
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())
    # Собираем текст из кусочков
    text = student['name'] + " | " + student['grade_name'] + " | " + date_from.strftime("%d.%m.%Y") + " - " \
           + date_to.strftime("%d.%m.%Y") + " | " + creator + " | " + subject['name']
    # Пишем заголовок
    pdf.cell(pdf.w - pdf.get_x() * 2, pdf.font_size * 2, txt=text, align='C', ln=1)
    # Рисуем еще один отчерк
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())
    # Отступаем еще раз
    pdf.ln(AFTER_HEADER_SPACE)


# Заголовок предмета
def title(pdf, subject):
    # Задаем шрифты
    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_font(SUBJECT_TITLE_FONT[0], size=SUBJECT_TITLE_FONT[1])
    # Рисуем заголовок
    pdf.cell(pdf.w - 2 * pdf.get_x(), pdf.font_size * 2, txt=subject['name'], align='C', ln=0)
    # Отступаем
    pdf.ln(AFTER_TITLE_SPACE)


def title_part(pdf, date_from, date_to, only_summative):
    date_format = "%d.%m.%Y"
    date_today = datetime.datetime.now().strftime(date_format)
    marks_param = "Only summative marks" if only_summative else "All student's marks"

    pdf.image("resources\\icon.png", x=10, y=12, w=50)

    pdf.set_font(TITLE_FONT[0], size=TITLE_FONT[1])
    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_xy(pdf.get_x() + pdf.w * 0.4, pdf.get_y())
    pdf.cell(pdf.w * 0.3, pdf.font_size * 2, txt="European Gymnasium", ln=2, align="L")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(INFO_FONT[0], size=INFO_FONT[1])
    pdf.cell(pdf.w * 0.3, pdf.font_size * 2, txt="Prepared: " + date_today, border=0, ln=2, align='L')

    pdf.cell(pdf.w * 0.3, pdf.font_size * 2, txt="From: " + date_from.strftime(date_format), border=0, ln=2, align='L')

    pdf.cell(pdf.w * 0.3, pdf.font_size * 2, txt="To: " + date_to.strftime(date_format), border=0, ln=2, align='L')
    # pdf.cell(113, 1, "",0,0,'L')
    pdf.cell(pdf.w * 0.3, pdf.font_size * 2, txt=marks_param, border=0, ln=1, align='L')

    pdf.ln(10)


def student_info(pdf, student_name, grade, account_name, comment):
    pdf.set_draw_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_line_width(0.5)

    line_delta = 5

    pdf.line(pdf.get_x() + line_delta, pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())

    pdf.set_font(STUDENT_INFO_FONT[0], size=STUDENT_INFO_FONT[1])
    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.cell(pdf.w * 0.2, pdf.font_size * 2, "Student name: ", border=0, ln=0, align='L')

    pdf.set_text_color(0, 0, 0)
    pdf.cell(pdf.w * 0.5, pdf.font_size * 2, student_name, border=0, ln=1, align='L')

    pdf.set_line_width(0.2)
    pdf.line(pdf.get_x() + line_delta, pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())

    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.cell(pdf.w * 0.2, pdf.font_size * 2, "Grade: ", border=0, ln=0, align='L')

    pdf.set_text_color(0, 0, 0)
    pdf.cell(pdf.w * 0.5, pdf.font_size * 2, grade, border=0, ln=1, align='L')

    pdf.line(pdf.get_x() + line_delta, pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())

    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.cell(pdf.w * 0.2, pdf.font_size * 2, "Adviser: ", border=0, ln=0, align='L')

    pdf.set_text_color(0, 0, 0)
    pdf.cell(pdf.w * 0.5, pdf.font_size * 2, account_name, border=0, ln=1, align='L')

    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())

    pdf.ln(pdf.font_size)

    if len(comment) > 0:
        pdf.set_font(INFO_FONT[0], size=INFO_FONT[1])
        pdf.cell(pdf.w * 0.5, pdf.font_size * 2, "Comments:", border=0, ln=1, align='L')

        pdf.set_xy(pdf.get_x() + 5, pdf.get_y())

        pdf.set_font(STUDENT_INFO_FONT[0], size=STUDENT_INFO_FONT[1])
        pdf.multi_cell(w=pdf.w - (pdf.get_x() * 2), h=pdf.font_size * 1.5, txt=comment, border=0, align='L')


def subjects_list_title(pdf):
    pdf.set_font(INFO_FONT[0], size=INFO_FONT[1])
    pdf.cell(9, 0, txt="", ln=0, align="L")
    pdf.cell(0, pdf.font_size * 1.8, txt="List Of Subjects:", ln=1, align="L")  # Добавил титульную надпись
    pdf.ln(pdf.font_size)

    pdf.set_draw_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_line_width(0.5)
    pdf.line(SUBJECT_OFFSET - 1, pdf.get_y(), pdf.w - SUBJECT_OFFSET + 1, pdf.get_y())


def draw_subject(pdf, subject, teachers):
    teacher_string = ', '.join([teacher['name'] for teacher in teachers])
    subject = subject['name']

    pdf.set_line_width(0.2)  # Нарисовал жирную верхнюю полоску и задал ширину поменьше
    pdf.set_text_color(BLUE_COLOR[0], BLUE_COLOR[1], BLUE_COLOR[2])
    pdf.set_font(STUDENT_INFO_FONT[0], size=STUDENT_INFO_FONT[1])  # Параметры для надписи предмета

    pdf.set_xy(SUBJECT_OFFSET, pdf.get_y() + pdf.font_size * 0.5)
    pdf.cell(0, pdf.font_size * 1.1, subject, ln=1,
             align="L")  # Задаю позицию курсора по статичному x и y из y_sub. Затем пишу название предмета

    pdf.set_text_color(0, 0, 0)
    pdf.set_font(SMALL_TEXT_FONT[0], size=SMALL_TEXT_FONT[1])  # Параметры для написания учителя

    pdf.set_xy(24, pdf.get_y())

    # Задаю позицию курсора по статичному x и y из y_tch. Затем пишу учителя привязанного к предмету
    pdf.cell(0, pdf.font_size * 2, teacher_string, ln=1, align="L")

    # Рисую линию по статичному x и длинне, за высоту беру y_line
    pdf.line(SUBJECT_OFFSET - 1, pdf.get_y(), pdf.w + 1 - SUBJECT_OFFSET, pdf.get_y())


def subjects_list_footer(pdf):
    pdf.set_line_width(0.5)
    # Рисую нижнюю жирную полоску. Отнимаю значение от высоты линии, чтобы она не съехала на деление вниз
    pdf.line(SUBJECT_OFFSET - 1, pdf.get_y(), pdf.w - SUBJECT_OFFSET + 1, pdf.get_y())


# API создание отчета
class ReportApi(Resource):
    def get(self):
        # Перечень аргументов
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('date_from', type=str, required=True, help="Date from is not given")
        parser.add_argument('date_to', type=str, required=True, help="Date to is not given")
        parser.add_argument('only_summative', type=int, required=True, help="Only summative is not given")
        parser.add_argument('subjects_list', type=str, required=True, help="Subjects list is not given")
        parser.add_argument('student_id', type=int, required=True, help="Student id is not given")
        parser.add_argument('comment', type=str)

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

        # Если нам не передали комментария, то пусть он будет пустой
        if args['comment'] is None:
            args['comment'] = ""
        else:
            try:
                # Иначе нам его передали в hex формате, чтобы не было кринж-символов
                args['comment'] = jshex_to_str(args['comment'])
            except Exception as e:
                print(e)
                return {
                    'result': 'Error!',
                    'error_message': str(e)
                }

        # Проверяем, есть ли у пользователя доступ
        status = check_access_token(args['access_token'])

        # Пробуем распарсить список предметов
        try:
            subjects_list = json.loads(args['subjects_list'])
        except:
            return {
                'result': 'Error!',
                'error_message': 'subjects_list cannot be converted to list'
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

        # Если пользователь авторизован
        if status[0]:
            # Вытаскиваем все данные, которые нам пригодятся
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            creator_name = Teachers.get_teacher(email)

            # такие поля: student['name'], student['id'], student['grade_name']
            student = Students.get_student(args['student_id'])

            my_subjects = [subject['id'] for subject in Subjects.get_student_subjects(student['id'])]

            # Собираем название файла
            filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_" + student['name'].replace(' ', '_') + "_by_" \
                       + creator_name.replace(" ", "_") + ".pdf"

            # Создаем ключ для скачивания этого отчета
            key = gen_key(filename)

            date_today = datetime.datetime.now()

            show_only_summative = args['only_summative'] == 1

            # Создаем pdf-ку, в которую будем писать
            pdf = FPDF()
            pdf.add_page()
            # Тут надо использовать русские шрифты
            pdf.add_font("Trebuchet MS", '', 'resources\\trebuchet.ttf', uni=True)
            # pdf.add_font("Trebuchet MS", '', 'resources\\trebuchet.ttf', uni=True)
            pdf.set_font("Trebuchet MS", size=12)

            title_part(pdf, date_from, date_to, show_only_summative)
            student_info(pdf, student['name'], student['grade_name'], creator_name, args['comment'])

            pdf.add_page()

            subjects_list_title(pdf)

            for subject in subjects_list:
                if subject not in my_subjects:
                    continue

                marks = Marks.get_marks(args['date_from'], args['date_to'], student['id'], subject,
                                        only_summative=show_only_summative)

                if len(marks) == 0:
                    continue

                # такие поля: teacher['email'], teacher['access_level'], teacher['name']
                # teachers - это список учителей
                teachers = Subjects.get_subjects_teachers(subject)

                # параметры: subject_obj['id'], subject_obj['name']
                subject_obj = Subjects.get_subject(subject)

                if subject_obj is None:
                    continue

                draw_subject(pdf, subject_obj, teachers)

            subjects_list_footer(pdf)

            pdf.set_xy(pdf.get_y(), pdf.h - 1)

            # Пишем оценки по каждому предмету
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
                marks = Marks.get_marks(args['date_from'], args['date_to'], student['id'], subject,
                                        only_summative=show_only_summative)

                if len(marks) == 0:
                    continue

                # Собираем таблицу с оценками
                table = generate_table(marks)

                # Рисуем эту таблицу и обновляем значение offset (см. документацию к draw_table)
                draw_table(pdf, table,
                           partial(page_hat, pdf, student, date_from, date_to, creator_name, subject_obj),
                           subject_obj)

            # Сохраняем в файл
            pdf.output(os.path.join("reports", filename))

            # Возвращаем ключ для скачивания
            return {
                'result': 'OK',
                'key': key
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
