import sys


# Основные константы проекта
class Metadata:
    GOOGLE_CLIENT_ID = '114697129947-ttoghpnvbb2pbp3mht3e11291ems9ska.apps.googleusercontent.com'
    MANAGEBAC_API_KEY = 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'
    MANAGEBAC_URL = 'https://api.managebac.com/v2/'
    DATABASE_USER = 'root'
    DATABASE_PASSWORD = 'root'
    JSON_WEB_REFRESH_TOKEN_LIFETIME = 60*24*60
    JSON_WEB_ACCESS_TOKEN_LIFETIME = 30
    SECRET_KEY = 'qwertyasdfghfdjhalifgf'
    DEBUG_MODE = True
    UPDATE_DATABASE_PERIOD = 24 * 3600
    MINIMUM_UPDATE_PERIOD = 2 * 3600
    REPORT_TABLE_WIDTH = 8
    TABLES_PER_PAGE = 4


# Ошибка, которую может выбросить функция
def error(message):
    if Metadata.DEBUG_MODE:
        sys.exit(message)
    else:
        print('Error!!!', message, '\n', sep='\n')


class Config(object):
    # Здесь будут настройки конкретно Flask App, пока что ничего
    pass
