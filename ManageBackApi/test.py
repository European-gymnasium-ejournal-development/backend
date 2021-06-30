import requests
import json
import googletrans
from google_trans_new import google_translator
from config import Metadata

translator = google_translator()
page = 1


while True:  
    url = Metadata.MANAGEBAC_URL + 'year-groups'
    headers = {'auth-token': Metadata.MANAGEBAC_API_KEY}
    payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
    y = requests.get(url, headers=headers, params=payload)
    grades = json.loads(y.text)
    page = page + 1  # добавляем 1 к параметру страницы
    for item1 in grades['year_groups']:  # создаём переменную в массиве студенты
        Grade_Name = item1['name']
        for student_id in item1['student_ids']:
            url2 = Metadata.MANAGEBAC_URL + 'students/' + str(student_id)
            headers2 = {'auth-token': Metadata.MANAGEBAC_API_KEY}
            y2 = requests.get(url2, headers=headers2)
            student = json.loads(y2.text)
            name_en = student['student']['first_name'] + ' ' + student['student']['last_name']
            name_ru = translator.translate(name_en, lang_src='en', lang_tgt='ru')
            print(student_id, name_ru, Grade_Name)
    if grades['meta']['current_page'] == grades['meta']['total_pages']:
        break
