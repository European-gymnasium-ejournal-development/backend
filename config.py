import sys


# Основные константы проекта
class Metadata:
    GOOGLE_CLIENT_ID = ''
    MANAGEBAC_API_KEY = ''
    MANAGEBAC_URL = 'https://api.managebac.com/v2/'
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''
    JSON_WEB_REFRESH_TOKEN_LIFETIME = 60*24*60
    JSON_WEB_ACCESS_TOKEN_LIFETIME = 30
    SECRET_KEY = ''
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


def upload_keys():
    env_file = open('settings.env')
    params = {data.split('=')[0]: data.split('=')[1][:-1] for data in env_file.readlines()}
    Metadata.MANAGEBAC_API_KEY = params['MANAGEBAC_API_KEY']
    Metadata.DATABASE_USER = params['DATABASE_USER']
    Metadata.DATABASE_PASSWORD = params['DATABASE_PASSWORD']
    Metadata.GOOGLE_CLIENT_ID = params['GOOGLE_CLIENT_ID']
    Metadata.SECRET_KEY = params['SECRET_KEY']


class Config(object):
    # Здесь будут настройки конкретно Flask App, пока что ничего
    pass
