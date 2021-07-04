import threading
import datetime
import os.path

mutex = threading.Lock()
date = datetime.datetime.today().strftime("%d.%m.%Y")
time = "12:10:10"
ip = "199.111.222"
email = 'asasas@gmail'
action = 'LogIn'
path = 'logs/' + date + '.txt'


def add_log(ip, time, email, action, path):
    mutex.acquire()
    if os.path.exists(path):
        file = open(path, 'a')
        file.write(ip + '/' + time + '/' + email + '/' + action + '|')
    else:
        file = open(path, 'w')
        file.write(ip + '/' + time + '/' + email + '/' + action + '|')
    mutex.release()


add_log(ip, time, email, action, path)
