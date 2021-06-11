from app.Database import db, Integer, Column, String, ForeignKey
# TaskType: 0 - formative, 1 - summative


class Task(db.Model):
    __tablename__ = 'tasks'
    id = Column('id', Integer, primary_key=True, unique=True)
    task_type = Column('type', Integer)
    subject_id = Column('subject_id', ForeignKey('subjects.id'))
    description = Column('description', String(60))

    def __init__(self, id, task_type, subject_id, description):
        self.id = id
        self.task_type = task_type
        self.description = description
        self.subject_id = subject_id

    def to_json(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'subject_id': self.subject_id,
            'description': self.description
        }


# Функция, добавляющая задание
# Если задание уже было, то данные будут обновлены
# task_type - тип задания (summative - 0/formative - 1)
# id - id задания в managebac
# subject_id - id предмета
# description - описание задания из managebac
def add_task(id, task_type, subject_id, description):
    existing_task = Task.query.filter_by(id=id)

    # Если создаем задачу с нуля
    if existing_task.first() is None:
        new_task = Task(id, task_type, subject_id, description)
        db.session.add(new_task)
    else:
        # Иначе обновляем значение записи
        existing_task.update(dict(task_type=task_type, subject_id=subject_id, description=description))

    db.session.commit()
