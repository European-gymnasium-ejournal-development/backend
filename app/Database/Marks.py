from app.Database import db, Integer, String, ForeignKey, Column, DateTime
import sys
# criteria: 0 - A, 1 - B, 2 - C, 3 - D


class Mark(db.Model):
    __tablename__ = 'marks'
    student_id = Column('student_id', ForeignKey('students.id'), primary_key=True, unique=False)
    criteria = Column('criteria', Integer)
    task_id = Column('task_id', ForeignKey('tasks.id'))
    mark = Column('mark', Integer)
    timestamp = Column('timestamp', DateTime)

    def __init__(self, student_id, criteria, task_id, mark, timestamp):
        self.student_id = student_id
        self.task_id = task_id
        self.timestamp = timestamp

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
            'timestamp': self.timestamp,
            'mark': self.mark,
            'criteria': self.criteria
        }


# Функция, добавляющая оценку за данное задание (task_id), выставленную в данное время (timestamp),
# данному студенту (student_id), по данному критерию (0 - 3) (criteria), с данным значением (mark)
# Если оценка с такими параметрами уже существовала, то обновляем данные
def add_mark(task_id, timestamp, student_id, criteria, mark):
    existing_mark = Mark.query.filter_by(student_id=student_id, timestamp=timestamp, task_id=task_id, criteria=criteria)

    # Если создаем оценку с нуля
    if existing_mark.first() is None:
        new_mark = Mark(student_id, criteria, task_id, mark, timestamp)
        db.session.add(new_mark)
    else:
        # Иначе обновляем значение оценки
        existing_mark.update(dict(mark=mark))

    db.session.commit()
