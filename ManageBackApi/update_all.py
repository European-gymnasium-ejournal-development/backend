from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks
from ManageBackApi.DB_teachers import update_teachers
from ManageBackApi.DB_students import update_students
from config import Metadata
import time
import multiprocessing
import threading


def update_all(update_period):
    import app.Database
    while True:
        print(update_period)
        print('started updating all')
        update_students()
        update_teachers()
        update_subjects_tasks_marks()
        print('everything is up to date')
        print('next update is in {} hours'.format(update_period // 3600))
        time.sleep(update_period)


update_process = None


def restart():
    global update_process
    if update_process is not None:
        update_process.terminate()
        update_process.join()
        update_process.close()
    update_process = multiprocessing.Process(name="update", target=update_all, args={Metadata.UPDATE_DATABASE_PERIOD})
    update_process.start()
