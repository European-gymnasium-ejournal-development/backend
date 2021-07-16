from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import JWRefreshTokens
import threading
import datetime
import os.path

# Мьютекс для отслеживания одновременной записи в логи
mutex = threading.Lock()


# Функция добавления логов
def add_log(ip, time, email, action):
    global mutex
    file_name = datetime.datetime.today().strftime("%Y-%m-%d") + ".log"
    path = os.path.join('logs', file_name)
    mutex.acquire()
    if os.path.exists(path):
        file = open(path, 'a')
    else:
        file = open(path, 'w')

    file.write(ip + '/' + time + '/' + email + '/' + action + '\n')
    file.close()
    mutex.release()


# API записи в логи
class LogsApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('action', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])
        # Проверяем, что пользователь авторизован
        if status[0] and args['action']:
            ip = str(reqparse.request.remote_addr)
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            action = args['action']
            time = datetime.datetime.now().strftime("%H:%M:%S")

            add_log(ip, time, email, action)

        return {}

