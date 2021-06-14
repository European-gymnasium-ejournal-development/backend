from app.Database import *
import sys

# Проверка баз данных
# Функции в этом файле позволяют посмотреть последние max_size записей в определенной таблице
# Если не задавать параметр max_size, то будут выведены все записи в таблице
# inspect_all выводит данные обо всех таблицах


def __inspect_table__(table_type, max_size):
    if issubclass(table_type, db.Model):
        print("Info from table {}s:".format(table_type.__name__))
        if max_size == -1:
            result = table_type.query.all()
        else:
            result = table_type.query.limit(max_size).all()

        for item in result:
            print(item.to_json())
    else:
        sys.exit("Problem with typing")


def inspect_students(max_size=-1):
    __inspect_table__(Student, max_size)


def inspect_marks(max_size=-1):
    __inspect_table__(Mark, max_size)


def inspect_teachers(max_size=-1):
    __inspect_table__(Teacher, max_size)


def inspect_subjects(max_size=-1):
    __inspect_table__(Subject, max_size)


def inspect_tasks(max_size=-1):
    __inspect_table__(Task, max_size)


def inspect_subject_to_student(max_size=-1):
    __inspect_table__(SubjectToStudentMapping, max_size)


def inspect_all(max_size=-1):
    inspect_students(max_size)
    inspect_subjects(max_size)
    inspect_teachers(max_size)
    inspect_subject_to_student(max_size)
    inspect_tasks(max_size)
    inspect_marks(max_size)
