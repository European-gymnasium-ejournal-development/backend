from app.Database.Tasks import add_task
from app.Database.Marks import add_mark
from app.Database.Subjects import add_subject
import requests
import json
from config import Metadata


def update_subjects_tasks_marks():
    print('started updating subjects, marks and tasks')
    page = 1
    while True:
        url = Metadata.MANAGEBAC_URL + 'classes'
        headers = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        y = requests.get(url, headers=headers, params=payload)
        subject = json.loads(y.text)
        page += 1
        for item1 in subject['classes']:
            subject_id = item1['id']
            subject_name = item1['name']
            url2 = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/students'
            headers2 = {'auth-token': Metadata.MANAGEBAC_API_KEY}
            y2 = requests.get(url2, headers=headers2, params=payload)
            student = json.loads(y2.text)

            print(subject_id, subject_name)
            print(student)

            add_subject(subject_id, subject_name, student['student_ids'])

            url3 = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/tasks'
            headers3 = {'auth-token': Metadata.MANAGEBAC_API_KEY}
            y3 = requests.get(url3, headers=headers3, params=payload)
            tasks = json.loads(y3.text)
            for item3 in tasks['tasks']:
                task_id = item3['id']
                task_date = item3['due_date']
                task_type = item3['task_type']
                task_description = item3['name']
                url4 = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/tasks/' + str(task_id) + '/students'
                headers4 = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                y4 = requests.get(url4, headers=headers4)
                task_marks = json.loads(y4.text)

                add_task(id=task_id,
                         task_type=task_type,
                         subject_id=subject_id,
                         description=task_description,
                         time_string=task_date)

                for item4 in task_marks['students']:
                    print(item4)
                    student_id = item4['id']
                    if any(x == 'criteria' for x in item4['assessments']):
                        for item5 in item4['assessments']['criteria']:
                            criteria = item5['label']
                            mark = item5['score']

                            add_mark(task_id=task_id,
                                     student_id=student_id,
                                     criteria=criteria,
                                     mark=mark)
                    elif any(x == 'points' for x in item4['assessments']):
                        criteria = '0'
                        mark = item4['assessments']['points']['score']
                        add_mark(task_id=task_id, student_id=student_id, criteria=criteria, mark=mark)

        if subject['meta']['current_page'] == subject['meta']['total_pages']:
            break
    print('finished updating subjects, marks and tasks')
