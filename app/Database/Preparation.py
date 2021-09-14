from app.Database import Marks, Students, Subjects, Tasks, Teachers, db


def prepare_for_update():
    Marks.Mark.query.update(dict(is_updated=False))
    Students.Student.query.update(dict(is_updated=False))
    Subjects.Subject.query.update(dict(is_updated=False))
    Subjects.SubjectsToTeachersMapping.query.update(dict(is_updated=False))
    Subjects.SubjectToStudentMapping.query.update(dict(is_updated=False))
    Tasks.Task.query.update(dict(is_updated=False))
    Teachers.Teacher.query.update(dict(is_updated=False))
    db.session.commit()


def remove_not_updated():
    Subjects.SubjectToStudentMapping.query.filter_by(is_updated=False).delete()
    Subjects.SubjectsToTeachersMapping.query.filter_by(is_updated=False).delete()
    Tasks.Task.query.filter_by(is_updated=False).delete()

    Marks.Mark.query.filter_by(is_updated=False).delete()
    Students.Student.query.filter_by(is_updated=False).delete()
    Teachers.Teacher.query.filter_by(is_updated=False).delete()
    Subjects.Subject.query.filter_by(is_updated=False).delete()
    db.session.commit()
