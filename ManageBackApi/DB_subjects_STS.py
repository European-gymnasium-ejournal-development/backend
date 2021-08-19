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
    page = 1
    while True:
        # Получаем информацию о предметах
        url_subjects = Metadata.MANAGEBAC_URL + 'classes'
        headers_subjects = {'auth-token': Metadata.MANAGEBAC_API_KEY}
        payload_subjects = {'page': page, 'per_page': '1000', 'archived': '(0)'}
        response_subjects = requests.get(url_subjects, headers=headers_subjects, params=payload_subjects)
        subjects = json.loads(response_subjects.text)
        page += 1
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

            # Получаем информацию об учениках, посещающих этот предмет
            url_students = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/students'
            headers_students = {'auth-token': Metadata.MANAGEBAC_API_KEY}
            response_students = requests.get(url_students, headers=headers_students, params=payload_subjects)
            students = json.loads(response_students.text)

            # print(subject_id, subject_name)
            # print(students)

            # Добавляем предмет в БД
            add_subject(subject_id, subject_name, students['student_ids'], subject_teachers)

            # Получачем все задания этого предмета
            url_tasks = Metadata.MANAGEBAC_URL + 'classes/' + str(subject_id) + '/tasks'
            headers_tasks = {'auth-token': Metadata.MANAGEBAC_API_KEY}
            response_tasks = requests.get(url_tasks, headers=headers_tasks, params=payload_subjects)
            tasks = json.loads(response_tasks.text)

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
                    comment = student_of_task['comments']
                    # Ищем критерий оценки в информации об ученике
                    if any(x == 'criteria' for x in student_of_task['assessments']):
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
                        if check_mark(mark, max_mark):
                            # TODO: добавить комментарий!
                            # TODO: если даже оценки нет, то передать туда пустую строку (и в max_mark тоже)
                            add_mark(task_id=task_id,
                                     student_id=student_id,
                                     criteria=criteria,
                                     mark=mark,
                                     max_mark=max_mark, comment="")

        # а точно это правильное условие? потому что, кажется, есть куча классов и учеников, у про которых известно мало
        if subjects['meta']['current_page'] == subjects['meta']['total_pages']:
            break
    print('finished updating subjects, marks and tasks')
