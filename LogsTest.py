import threading
import datetime
import os.path
import app.ApiHandlers.Logs


date = datetime.datetime.today().strftime("%d.%m.%Y")
time = "12:10:10"
ip = "199.111.222"
email = 'asasas@gmail'
action = 'LogIn'

app.ApiHandlers.Logs.add_log(ip, time, email, action)
