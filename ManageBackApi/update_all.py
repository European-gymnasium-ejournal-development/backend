from create.config import Metadata, upload_keys
upload_keys()

from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks
from ManageBackApi.DB_teachers import update_teachers
from ManageBackApi.DB_students import update_students

import time
import datetime
import threading
import app.Database
import app.Database.Preparation

should_restart = False


def update_all(update_period):
    while True:
        if should_restart:
            return
        app.Database.Preparation.prepare_for_update()
        start_update_time = datetime.datetime.now()
        # print(update_period)
        print('started updating all')
        update_students()
        update_teachers()
        update_subjects_tasks_marks()
        print('everything is up to date')
        print('next update is in {} hours'.format(update_period // 3600))
        Metadata.LAST_UPDATE = start_update_time

        app.Database.Preparation.remove_not_updated()
        time.sleep(update_period)


update_process = None


def restart():
    global update_process, should_restart
    should_restart = True
    if update_process is not None:
        update_process.join()
    should_restart = False
    update_process = threading.Thread(name="update", target=update_all, args=(Metadata.UPDATE_DATABASE_PERIOD,))
    update_process.start()
