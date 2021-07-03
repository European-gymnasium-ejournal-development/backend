from app.Database.Students import add_student
import requests
import json
from googletrans import Translator
from google_trans_new import google_translator
import re
from config import Metadata


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
        url = Metadata.MANAGEBAC_URL + 'year-groups'
        headers = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        y = requests.get(url, headers=headers, params=payload)
        grades = json.loads(y.text)
        page = page + 1  # добавляем 1 к параметру страницы

        for item1 in grades['year_groups']:  # создаём переменную в массиве студенты
            grade_name = item1['name']
            for student_id in item1['student_ids']:
                url2 = Metadata.MANAGEBAC_URL + 'students/' + str(student_id)
                headers2 = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                y2 = requests.get(url2, headers=headers2)
                student = json.loads(y2.text)
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
