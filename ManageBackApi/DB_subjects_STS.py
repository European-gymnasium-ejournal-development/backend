from app.Database.Tasks import add_task
from app.Database.Marks import add_mark
from app.Database.Subjects import add_subject
import requests
import json
from create.config import Metadata


def check_mark(mark, max_mark):
    return mark is not None and max_mark is not None


def update_subjects_tasks_marks():
    print('started updating subjects, marks and tasks')
    page_subject = 0
    last_page_subject = -1
    while page_subject != last_page_subject:
        page_subject += 1
        # Получаем информацию о предметах
        url_subjects = Metadata.MANAGEBAC_URL + 'classes'
        headers_subjects = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload_subjects = {'page': page_subject, 'per_page': '1000'}
        response_subjects = requests.get(url_subjects, headers=headers_subjects, params=payload_subjects)
        subjects = json.loads(response_subjects.text)
        last_page_subject = subjects['meta']['total_pages']
        # print(subjects)

        # Итерируемся по предметам
        for subject_index, subject in enumerate(subjects['classes']):
            # print(str(subject_index + 1) + " of " + str(len(subjects['classes'])))
            # print(subject)
            subject_id = subject['id']
            subject_name = subject['name']
            subject_teachers = []
            # Перебираем всех учителей предмета
            for teacher in subject['teachers']:
                if teacher['show_on_reports']:
                    subject_teachers.append(teacher['teacher_id'])

            page_student = 0
            last_page_student = -1
            while page_student != last_page_student:
                page_student += 1
                # Получаем информацию об учениках, посещающих этот предмет
                url_students = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/students'
                headers_students = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                payload_students = {'page': page_student, 'per_page': '1000'}
                response_students = requests.get(url_students, headers=headers_students, params=payload_students)
                students = json.loads(response_students.text)

                last_page_student = students['meta']['total_pages']
                # print(students)
                # Добавляем предмет в БД
                add_subject(subject_id, subject_name, students['student_ids'], subject_teachers)

                page_tasks = 0
                total_pages_tasks = -1
                while page_tasks != total_pages_tasks:
                    page_tasks += 1
                    # Получачем все задания этого предмета
                    url_tasks = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/tasks'
                    headers_tasks = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                    payload_tasks = {'page': page_tasks, 'per_page': '1000'}
                    response_tasks = requests.get(url_tasks, headers=headers_tasks, params=payload_tasks)
                    tasks = json.loads(response_tasks.text)

                    # print(tasks)
                    # print(headers_tasks, url_tasks)

                    if 'tasks' not in tasks.keys() or 'meta' not in tasks.keys():
                        if total_pages_tasks == -1:
                            break
                        continue

                    total_pages_tasks = tasks['meta']['total_pages']
                    # print(tasks['meta']['total_count'])
                    if tasks['meta']['total_pages'] > 1:
                        print("AAAAAA total_pages is: {}".format(tasks['meta']['total_pages']))
                    # print(tasks)

                    # Итерируемся по заданиям
                    for task in tasks['tasks']:
                        # print(task)
                        task_id = task['id']
                        task_date = task['due_date']
                        task_type = task['task_type']
                        task_description = task['name']

                        # Добавляем в БД задание
                        add_task(id=task_id,
                                 task_type=task_type,
                                 subject_id=subject_id,
                                 description=task_description,
                                 time_string=task_date)

                        # Получаем информацию об учениках, выполнивших задание
                        url_students_of_task = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/tasks/' + str(task_id) + '/students'
                        headers_students_of_task = {'auth-token': Metadata.MANAGEBAC_API_KEY}
                        response_students_of_task = requests.get(url_students_of_task, headers=headers_students_of_task)
                        students_of_task = json.loads(response_students_of_task.text)

                        # Итерируемся по ученикам
                        for student_of_task in students_of_task['students']:
                            # print(student_of_task)
                            student_id = student_of_task['id']
                            # print(student_of_task)

                            # Ищем критерий оценки в информации об ученике
                            if any(x == 'criteria' for x in student_of_task['assessments']):
                                comment = student_of_task['assessments']['comments']
                                # Если находим, то итерируемся по всем критериям, по которым выставлена оценка
                                for mark_json in student_of_task['assessments']['criteria']:
                                    # Добавляем оценку в БД
                                    criteria = mark_json['label']
                                    mark = mark_json['score']
                                    max_mark = 8
                                    if check_mark(mark, max_mark):
                                        # TODO: добавить комментарий!
                                        # TODO: если даже оценки нет, то передать туда пустую строку (и в max_mark тоже)
                                        add_mark(task_id=task_id,
                                                 student_id=student_id,
                                                 criteria=criteria,
                                                 mark=mark,
                                                 max_mark=max_mark, comment=comment)
                            # Если не находим, то добавляем значение без критерия
                            elif any(x == 'points' for x in student_of_task['assessments']):
                                criteria = '0'
                                mark = student_of_task['assessments']['points']['score']
                                max_mark = student_of_task['assessments']['points']['max_score']
                                comment = student_of_task['assessments']['comments']
                                if check_mark(mark, max_mark):
                                    # TODO: добавить комментарий!
                                    # TODO: если даже оценки нет, то передать туда пустую строку (и в max_mark тоже)
                                    add_mark(task_id=task_id,
                                             student_id=student_id,
                                             criteria=criteria,
                                             mark=mark,
                                             max_mark=max_mark, comment=comment)

    print('finished updating subjects, marks and tasks')
