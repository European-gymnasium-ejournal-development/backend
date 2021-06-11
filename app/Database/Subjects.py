from app.Database import db, Column, Integer, String, ForeignKey


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = Column('id', Integer, primary_key=True, unique=True)
    name = Column('name', String(60), unique=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class SubjectToStudentMapping(db.Model):
    __tablename__ = 'subject_to_student'
    subject_id = Column('subject_id', ForeignKey('subjects.id'))
    student_id = Column('student_id', ForeignKey('students.id'), primary_key=True, unique=False)

    def __init__(self, subject_id, student_id):
        self.student_id = subject_id
        self.student_id = student_id


# Функция, добавляющая предмет в БД
# Если такой предмет уже существовал, то данные будут обновлены
# id - id предмета в ManageBac
# subject_name - название предмета
# students_ids - список id студентов, посещающих курс
def add_subject(id, subject_name, students_ids):
    existing_subject = Subject.query.filter_by(id=id)

    # Если создаем предмет с нуля
    if existing_subject.first() is None:
        new_subject = Subject(id, subject_name)
        db.session.add(new_subject)
    else:
        # Иначе обновляем значение записи
        existing_subject.update(dict(name=subject_name))

    # Теперь обновляем учеников
    for student in students_ids:
        record = SubjectToStudentMapping.query.filter_by(student_id=student, subject_id=id)
        if record.first() is None:
            new_record = SubjectToStudentMapping(id, student)
            db.session.add(new_record)

    db.session.commit()
