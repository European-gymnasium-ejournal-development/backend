

print("Введите время в минутах")
x = input()
time = x*60
while True:
    from DB_subjects_STS import update_subjects_tasks_marks
    from DB_teachers import update_teachers
    from DB_students import update_students
    import time
    print('aaa')
    update_subjects_tasks_marks()
    update_teachers()
    update_students()
    time.sleep(time)
