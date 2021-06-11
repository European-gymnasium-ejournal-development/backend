from app.Database.Teachers import add_teacher, Teacher
from app.Database.Students import add_student, Student
from app.Database.Tasks import add_task, Task
from app.Database.Marks import add_mark, Mark
from app.Database.Subjects import add_subject, Subject, SubjectToStudentMapping
from datetime import datetime


def test_database():
    print('the journey begins)))')
    add_teacher(0, "test", "test@test.com", 3)
    print(Teacher.query.filter_by().all())
    print('test finished1')
    add_student(1, "qwerty", "10A")
    print(Student.query.filter_by().all())
    print('test finished2')
    add_subject(2, "Algebra", [1])
    print(SubjectToStudentMapping.query.filter_by().all())
    print(Subject.query.filter_by().all())
    print('test finished3')
    add_task(3, 1, 2, "Good task")
    print(Task.query.filter_by().all())
    print('test finished4')
    add_mark(3, datetime.now(), 1, 2, 7)
    print(Mark.query.filter_by().all())
    print('test finished')
