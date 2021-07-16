from sqlalchemy.orm import load_only
from app.Database.Students import Student
from app.Database.Teachers import Teacher
from app.Database import db, Column, Integer, String, ForeignKey


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = Column('id', Integer, primary_key=True, unique=True)
    name = Column('name', String(512), unique=False)

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
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    subject_id = Column('subject_id', ForeignKey('subjects.id'))
    student_id = Column('student_id', ForeignKey('students.id'))

    def __init__(self, subject_id, student_id):
        self.subject_id = subject_id
        self.student_id = student_id

    def to_json(self):
        return {
            'student_id': self.student_id,
            'subject_id':self.subject_id
        }


# Соответствие учителей предметам, которые они ведут
class SubjectsToTeachersMapping(db.Model):
    __tablename__ = "subjects_to_teachers"
    id = Column('id', Integer, autoincrement=True, primary_key=True, unique=True)
    subject_id = Column('subject_id', ForeignKey("subjects.id"))
    teacher_id = Column('teacher_id',  ForeignKey("teachers.id"))

    def __init__(self, subject_id, teacher_id):
        self.subject_id = subject_id
        self.teacher_id = teacher_id

    def to_json(self):
        return {
            "subject_id": self.subject_id,
            "teacher_id": self.teacher_id
        }


# Функция, добавляющая предмет в БД
# Если такой предмет уже существовал, то данные будут обновлены
# id - id предмета в ManageBac
# subject_name - название предмета
# students_ids - список id студентов, посещающих курс
# teachers - список id учителей, которые ведут курс
def add_subject(id, subject_name, students_ids, teachers):
    existing_subject = Subject.query.filter_by(id=id)

    # Если создаем предмет с нуля
    if existing_subject.first() is None:
        new_subject = Subject(id, subject_name)
        db.session.add(new_subject)
    else:
        # Иначе обновляем значение записи
        existing_subject.update(dict(name=subject_name))

    db.session.commit()

    # Теперь обновляем учеников
    for student in students_ids:
        record = SubjectToStudentMapping.query.filter_by(student_id=student, subject_id=id)
        student_record = Student.query.filter_by(id=student)
        if record.first() is None and student_record.first() is not None:
            new_record = SubjectToStudentMapping(id, student)
            db.session.add(new_record)

    # Теперь добавляем учителей в предмет
    for teacher in teachers:
        record = SubjectsToTeachersMapping.query.filter_by(teacher_id=teacher, subject_id=id)
        teacher_record = Teacher.query.filter_by(id=teacher)

        if record.first() is None and teacher_record.first() is not None:
            new_record = SubjectsToTeachersMapping(id, teacher)
            db.session.add(new_record)

    db.session.commit()


# Функция получения предметов, посещаемых учеником
# Возвращает список словарей
def get_student_subjects(student_id):
    request_subject_ids = SubjectToStudentMapping.query.with_entities(SubjectToStudentMapping.subject_id).\
        filter_by(student_id=student_id)

    request_subjects = Subject.query.filter(Subject.id.in_(request_subject_ids))
    return [item.to_json() for item in request_subjects.all()]


# Получение списка учителей, которые ведут курс с id subject_id
def get_subjects_teachers(subject_id):
    request = SubjectsToTeachersMapping.query.filter_by(subject_id=subject_id)\
        .with_entities(SubjectsToTeachersMapping.teacher_id)

    teachers_request = Teacher.query.filter(Teacher.id.in_(request))
    return [item.to_json() for item in teachers_request.all()]


# Получение информации о предмете по его id
def get_subject(subject_id):
    request = Subject.query.filter_by(id=subject_id).first()
    if request is not None:
        return request.to_json()
    else:
        return None
