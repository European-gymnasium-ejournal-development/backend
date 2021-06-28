import requests
import json
import googletrans
from google_trans_new import google_translator
translator = google_translator()  
page = 1
while True:  
    url = 'https://api.managebac.com/v2/year-groups'
    headers = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
    payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
    y = requests.get(url, headers=headers, params=payload)
    grades = json.loads(y.text)
    page = page + 1  # добавляем 1 к параметру страницы
    for item1 in grades['year_groups']:  # создаём переменную в массиве студенты
        Grade_Name = item1['name']
        for student_id in item1['student_ids']:
            url2 = 'https://api.managebac.com/v2/students/' + str(student_id)
            headers2 = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
            y2 = requests.get(url2, headers=headers2)
            student = json.loads(y2.text)
            name_en = student['student']['first_name'] + ' ' + student['student']['last_name']
            name_ru = translator.translate(name_en,lang_src='en',lang_tgt='ru')
            print (student_id,name_ru,Grade_Name)
    if grades['meta']['current_page'] == grades['meta']['total_pages']:
        break
