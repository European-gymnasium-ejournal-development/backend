from app.Database.Students import add_student
import requests
import json
from googletrans import Translator
from google_trans_new import google_translator
import re
from create.config import Metadata


# Получает список из словарей с полями name, grade, id,
# возвращает такой же список, но все имена в нем переведены на русский
def translate_names(students):
    english_name = r"[A-Za-z]+"
    translator = google_translator()

    new_students = []
    for student in students:
        new_students.append(student)
        if re.match(english_name, student['name']):
            translated = translator.translate(student['name'].title(), lang_src='en', lang_tgt='ru')
            new_students[-1]['name'] = translated.title()
    return new_students


def update_students():
    print('started updating students')
    page = 1
    total_students = []
    while True:
        # Получаем из API ManageBac классы
        url_grades = Metadata.MANAGEBAC_URL + 'year-groups'
        headers_grades = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload_grades = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        response_grades = requests.get(url_grades, headers=headers_grades, params=payload_grades)
        grades = json.loads(response_grades.text)
        page += 1  # добавляем 1 к параметру страницы

        # Итерируемся по классам и по их ученикам
        for grade in grades['year_groups']:
            grade_name = grade['name']
            for student_id in grade['student_ids']:
                # Получаем данные об ученике
                url_students = Metadata.MANAGEBAC_URL + 'students/' + str(student_id)
                headers_students = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                response_students = requests.get(url_students, headers=headers_students)
                student = json.loads(response_students.text)
                name_en = student['student']['first_name'] + ' ' + student['student']['last_name']
                total_students.append({'id': student_id, 'grade': grade_name, 'name': name_en})

        if grades['meta']['current_page'] == grades['meta']['total_pages']:
            break
    print('finished loading data')
    # Перевод не понадобился
    # total_students = translate_names(total_students)
    for student in total_students:
        add_student(student['id'], student['name'], student['grade'])

    print('finished updating students')
