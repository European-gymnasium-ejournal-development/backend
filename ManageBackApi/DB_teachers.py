from app.Database import Teachers
import requests
import json
from config import Metadata


def update_teachers():
    print('updating teachers')
    page = 1
    while True:
        url = Metadata.MANAGEBAC_URL + 'teachers'
        headers = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        y = requests.get(url, headers=headers, params=payload)
        teachers = json.loads(y.text)
        page = page + 1  # добавляем 1 к параметру страницы
        for item1 in teachers['teachers']:  # создаём переменную в массиве студенты
            teacher_id = item1['id']
            name = item1['first_name'] + ' ' + item1['last_name']
            email = item1['email']
            Teachers.add_teacher(id=teacher_id, name=name, email=email, access_level=Teachers.AccessLevel.CASUAL_ACCESS)
        if teachers['meta']['current_page'] == teachers['meta']['total_pages']:
            break
    print('finished updating teachers')
