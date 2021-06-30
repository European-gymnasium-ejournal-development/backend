from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks
from ManageBackApi.DB_teachers import update_teachers
from ManageBackApi.DB_students import update_students
import time


def update_all():
    print('started updating all')
    update_teachers()
    update_students()
    update_subjects_tasks_marks()
    print('everything is up to date')
