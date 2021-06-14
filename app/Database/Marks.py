from datetime import datetime

from app.Database import db, Integer, String, ForeignKey, Column, DateTime, Tasks
import sys
# criteria: 0 - A, 1 - B, 2 - C, 3 - D


class Mark(db.Model):
    __tablename__ = 'marks'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    student_id = Column('student_id', ForeignKey('students.id'), unique=False)
    criteria = Column('criteria', Integer)
    task_id = Column('task_id', ForeignKey('tasks.id'))
    mark = Column('mark', Integer)

    def __init__(self, student_id, criteria, task_id, mark):
        self.student_id = student_id
        self.task_id = task_id

        if isinstance(criteria, int):
            if 0 <= criteria <= 3:
                self.criteria = criteria
            else:
                sys.exit('criteria should be in interval 0 to 3')
        else:
            sys.exit('criteria should be an integer')

        if isinstance(mark, int):
            if 1 <= mark <= 8:
                self.mark = mark
            else:
                sys.exit('mark should be in interval 1 to 8')
        else:
            sys.exit('mark should be an integer')

    def to_json(self):
        return {
            'student_id': self.student_id,
            'task_id': self.task_id,
            'mark': self.mark,
            'criteria': self.criteria
        }


# Функция, добавляющая оценку за данное задание (task_id),
# выставленную данному студенту (student_id), по данному критерию (0 - 3) (criteria), с данным значением (mark)
# Если оценка с такими параметрами уже существовала, то обновляем данные
def add_mark(task_id, student_id, criteria, mark):
    existing_mark = Mark.query.filter_by(student_id=student_id, task_id=task_id, criteria=criteria)

    # Если создаем оценку с нуля
    if existing_mark.first() is None:
        new_mark = Mark(student_id, criteria, task_id, mark)
        db.session.add(new_mark)
    else:
        # Иначе обновляем значение оценки
        existing_mark.update(dict(mark=mark))

    db.session.commit()


def user_input_time_to_datetime(time):
    return datetime.strptime(time, '%d.%m.%Y')


# Функция получения всех оценок ученика по предмету за период
# Возвращает список словарей
def get_marks(time_from, time_to, student_id, subject_id):
    timestamp_begin = user_input_time_to_datetime(time_from)
    timestamp_end = user_input_time_to_datetime(time_to)

    request_tasks = Tasks.Task.query.filter(Tasks.Task.timestamp >= timestamp_begin)\
                                    .filter(Tasks.Task.timestamp <= timestamp_end)\
                                    .filter_by(subject_id=subject_id)\
                                    .with_entities(Tasks.Task.id)

    request_marks = Mark.query.filter_by(student_id=student_id).filter(Mark.task_id.in_(request_tasks))
    mark_list = [item.to_json() for item in request_marks.all()]

    for index, mark in enumerate(mark_list):
        task = Tasks.Task.query.filter_by(id=mark['task_id']).first()
        mark['type'] = task.task_type
        mark['timestamp'] = task.timestamp
        mark['description'] = task.description

        mark_list[index] = mark

    return mark_list
