from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks
from ManageBackApi.DB_teachers import update_teachers
from ManageBackApi.DB_students import update_students
import time

def update_all(time):
    while True:
        print(time)
        print('started updating all')
        update_subjects_tasks_marks
        update_teachers
        update_students
        print('everything is up to date')
        time.sleep(time)

p1=multiprocessing.Process(name="update", target = update_all, args=time )
