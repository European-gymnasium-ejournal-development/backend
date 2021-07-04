from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks
from ManageBackApi.DB_teachers import update_teachers
from ManageBackApi.DB_students import update_students
from multiprocessing import Process


def update_all():
    if __name__=="__main__":
        print('started updating all')
        p1=Process(target=update_subjects_tasks_marks)
        p2=Process(target=update_teachers)
        p3=Process(target=update_students)
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()
        print('everything is up to date')

