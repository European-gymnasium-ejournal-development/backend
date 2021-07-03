from app.Database import db, Integer, Column, String, ForeignKey, DateTime
from datetime import datetime
from datetime import timedelta

# TaskType: 0 - formative, 1 - summative
TASK_TYPES = {0: 'formative', 1: 'summative'}


def tasktype_to_name(tasktype):
    return TASK_TYPES[tasktype]


def name_to_tasktype(name):
    for key in TASK_TYPES.keys():
        if TASK_TYPES[key] == name:
            return key
    raise AttributeError("No such task name")


class Task(db.Model):
    __tablename__ = 'tasks'
    id = Column('id', Integer, primary_key=True, unique=True)
    task_type = Column('type', Integer)
    subject_id = Column('subject_id', ForeignKey('subjects.id'))
    description = Column('description', String(16000))
    timestamp = Column('timestamp', DateTime)

    def __init__(self, id, task_type, subject_id, description, timestamp):
        self.id = id
        self.task_type = task_type
        self.description = description
        self.subject_id = subject_id
        self.timestamp = timestamp

    def to_json(self):
        return {
            'id': self.id,
            'task_type': tasktype_to_name(self.task_type),
            'subject_id': self.subject_id,
            'description': self.description,
            'timestamp': self.timestamp.strftime("%Y-%m-%d")
        }


# Функция перевода времени в виде строки типа 2020-09-09T15:10:00+03:00
# В объект datetime для вставки в БД
def time_to_datetime(time_string):
    datetime_obj = datetime.strptime(time_string.split('+')[0], '%Y-%m-%dT%H:%M:%S')
    datetime_delta = datetime.strptime(time_string.split('+')[1], '%H:%M')
    delta = timedelta(hours=datetime_delta.hour, minutes=datetime_delta.minute)
    return datetime_obj + delta


# Функция, добавляющая задание
# Если задание уже было, то данные будут обновлены
# task_type - тип задания (summative - 0/formative - 1)
# id - id задания в managebac
# subject_id - id предмета
# description - описание задания из managebac
# time - строка со временем дедлайна задания
def add_task(id, task_type, subject_id, description, time_string):
    task_type = name_to_tasktype(task_type)

    existing_task = Task.query.filter_by(id=id)
    timestamp = time_to_datetime(time_string)

    # Если создаем задачу с нуля
    if existing_task.first() is None:
        new_task = Task(id, task_type, subject_id, description, timestamp)
        db.session.add(new_task)
    else:
        # Иначе обновляем значение записи
        existing_task.update(dict(task_type=task_type,
                                  subject_id=subject_id,
                                  description=description,
                                  timestamp=timestamp))

    db.session.commit()
