from app.Database import Teachers
import requests
import json
from config import Metadata


def update_teachers():
    print('updating teachers')
    page = 1
    while True:
        # Получаем информацию об учителях
        url = Metadata.MANAGEBAC_URL + 'teachers'
        headers = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        response = requests.get(url, headers=headers, params=payload)
        teachers = json.loads(response.text)
        page = page + 1  # добавляем 1 к параметру страницы
        # Итерируемся по учителям и добавляем их в БД
        for teacher in teachers['teachers']:
            teacher_id = teacher['id']
            name = teacher['first_name'] + ' ' + teacher['last_name']
            email = teacher['email']
            Teachers.add_teacher(id=teacher_id, name=name, email=email, access_level=Teachers.AccessLevel.CASUAL_ACCESS)
        if teachers['meta']['current_page'] == teachers['meta']['total_pages']:
            break
    print('finished updating teachers')
