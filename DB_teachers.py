
def update_teachers():
    from app.Database.Teachers import add_teacher
    import requests
    import json
    page = 1
    while True:  
        url = 'https://api.managebac.com/v2/teachers'
        headers = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
        payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        y = requests.get(url, headers=headers, params=payload)
        teachers = json.loads(y.text)
        page = page + 1  
        for item1 in teachers['teachers']:  
            teacher_id = item1['id']
            name = item1['first_name'] + ' ' + item1['last_name']
            email = item1['email']
            add_teacher(id=teacher_id,name=name,email=email,access_level=1)
        if teachers['meta']['current_page'] == teachers['meta']['total_pages']:
            break

