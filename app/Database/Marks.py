from datetime import datetime

from app.Database import db, Integer, String, ForeignKey, Column, DateTime, Tasks, Students
from create.config import error
# criteria: 1 - A, 2 - B, 3 - C, 4 - D, 0 - No criteria

criteria_ids = {'A': 1, 'B': 2, 'C': 3, 'D': 4, '0': 0}


def criteria_to_id(criteria):
    if criteria in criteria_ids.keys():
        return criteria_ids[criteria]
    else:
        raise AttributeError("Criteria argument does not match any of possible criteria")


def id_to_criteria(id):
    for key in criteria_ids.keys():
        value = criteria_ids[key]
        if value == id:
            return key
    error("Id argument does not match any criteria")


class Mark(db.Model):
    __tablename__ = 'marks'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    student_id = Column('student_id', ForeignKey('students.id'), unique=False)
    criteria = Column('criteria', Integer)
    task_id = Column('task_id', ForeignKey('tasks.id'))
    mark = Column('mark', String(16))
    max_mark = Column('max_mark', String(16))

    def __init__(self, student_id, criteria, task_id, mark, max_mark):
        self.student_id = student_id
        self.task_id = task_id
        self.max_mark = str(max_mark)
        self.mark = str(mark)

        if isinstance(criteria, int):
            if 0 <= criteria <= 4:
                self.criteria = criteria
            else:
                error('criteria should be in interval 0 to 3')
        else:
            error('criteria should be an integer')

    def to_json(self):
        return {
            'student_id': self.student_id,
            'task_id': self.task_id,
            'mark': self.mark,
            'criteria': id_to_criteria(self.criteria),
            'max_mark': self.max_mark
        }


# Функция, добавляющая оценку за данное задание (task_id),
# выставленную данному студенту (student_id), по данному критерию (A, B, C, D, 0) (criteria), с данным значением (mark)
# Если оценка с такими параметрами уже существовала, то обновляем данные
def add_mark(task_id, student_id, criteria, mark, max_mark):
    try:
        criteria = criteria_to_id(criteria)
    except AttributeError:
        return

    student_record = Students.Student.query.filter_by(id=student_id)
    task_record = Tasks.Task.query.filter_by(id=task_id)

    if student_record.first() is None or task_record.first() is None:
        return

    existing_mark = Mark.query.filter_by(student_id=student_id, task_id=task_id, criteria=criteria)

    # Если создаем оценку с нуля
    if existing_mark.first() is None:
        new_mark = Mark(student_id, criteria, task_id, mark, max_mark)
        db.session.add(new_mark)
    else:
        # Иначе обновляем значение оценки
        existing_mark.update(dict(mark=str(mark), max_mark=str(max_mark)))

    db.session.commit()


def user_input_time_to_datetime(time):
    return datetime.strptime(time, '%d.%m.%Y')


# Функция получения всех оценок ученика по предмету за период
# Возвращает список словарей
def get_marks(time_from, time_to, student_id, subject_id, only_summative=False):
    timestamp_begin = user_input_time_to_datetime(time_from)
    timestamp_end = user_input_time_to_datetime(time_to)

    # Запрос такой
    # select * from marks m inner join tasks t on m.task_id = t.id where (m.student_id=student_id
    # and t.timestamp >= timestamp_begin and t.timestamp <= timestamp_end and subject_id=subject_id)

    request_tasks = Tasks.Task.query.filter(Tasks.Task.timestamp >= timestamp_begin)\
                                    .filter(Tasks.Task.timestamp <= timestamp_end)\
                                    .filter_by(subject_id=subject_id)

    if only_summative:
        request_tasks = request_tasks.filter_by(task_type=Tasks.name_to_tasktype('summative'))

    request_tasks = request_tasks.with_entities(Tasks.Task.id)

    # request_marks = Mark.query.join(Tasks.Task, Mark.task_id == Tasks.Task.id)\
    #    .filter(Mark.student_id == student_id).filter(Tasks.Task.timestamp <= timestamp_end)\
    #    .filter(Tasks.Task.timestamp >= timestamp_begin).filter(Tasks.Task.subject_id == subject_id)

    request_marks = Mark.query.filter_by(student_id=student_id).filter(Mark.task_id.in_(request_tasks))

    mark_list = []

    for mark in request_marks.all():
        mark_js = mark.to_json()
        # task_js = task.to_json()

        # full_obj = {key: value for (key, value) in (mark_js.items() + task_js.items())}

        # mark_list.append(full_obj)
        task = Tasks.Task.query.filter_by(id=mark_js['task_id']).first()
        mark_js['type'] = Tasks.tasktype_to_name(task.task_type)
        mark_js['timestamp'] = task.timestamp.strftime("%Y-%m-%d")
        mark_js['description'] = task.description

        mark_list.append(mark_js)

        # mark_list[index] = mark

    return mark_list
