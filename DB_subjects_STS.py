def update_subjects_tasks_marks():
    from app.Database.Tasks import add_task
    from app.Database.Marks import add_mark
    from app.Database.Subjects import add_subject
    import requests
    import json
    page = 1
    while True:  
        url = 'https://api.managebac.com/v2/classes'
        headers = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
        payload = {'page': page, 'per_page': '1000'}
        y = requests.get(url, headers=headers, params=payload)
        subject = json.loads(y.text)
        page = page + 1  
        for item1 in subject['classes']:  
            subject_id = item1['id']
            subject_name = item1['name']
            url2 = 'https://api.managebac.com/v2/classes/' + str(subject_id) + '/students'
            headers2 = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
            y2 = requests.get(url2, headers=headers2)
            student = json.loads(y2.text)
            add_subject(subject_id, subject_name, student['student_ids'])
            url3 = 'https://api.managebac.com/v2/classes/' + str(subject_id) + '/tasks'
            headers3 = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
            y3 = requests.get(url3, headers=headers3)
            tasks = json.loads(y3.text)
            for item3 in tasks['tasks']:
                task_id = item3['id']
                task_date = item3['due_date']
                task_type = item3['task_type']
                task_description = item3['name']
                url4 = 'https://api.managebac.com/v2/classes/' + str(subject_id) + '/tasks/' + str(task_id) + '/students'
                headers4 = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
                y4 = requests.get(url4, headers=headers4)
                task_marks = json.loads(y4.text)
                add_task (id=task_id,task_type=task_type,subject_id=subject_id,description=task_description)
                for item4 in task_marks['students']:
                    student_id = item4['id']
                    print(item4)
                    if any( x == 'criteria' for x in item4['assessments'] ):
                        for item5 in item4['assessments']['criteria']:
                            criteria = item5['label']
                            mark = item5['score']
                            add_mark(task_id=task_id,timestamp=task_date, student_id=student_id, criteria=criteria, mark=mark)
        if subject['meta']['current_page'] == subject['meta']['total_pages']:
            break
