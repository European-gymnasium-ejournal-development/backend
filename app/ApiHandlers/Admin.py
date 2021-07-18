from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Teachers, JWRefreshTokens
from create.config import Metadata
from ManageBackApi import update_all
import os
import sys
from flask import send_file, redirect
import datetime


# Все функции администраторского API


# Обработка запроса от пользователя, которая используется во всех функциях админа
# Проверяет, что у пользователя достаточно прав на доступ к функциям админа
# Возвращает либо http-response с уведомлением об ошибке, либо None, если все хорошо
def standart_processing(parser):
    parser.add_argument('access_token', location='cookies', type=str)

    args = parser.parse_args()
    status = check_access_token(args['access_token'])

    if status[0]:
        email = JWRefreshTokens.parse_email_from_token(args['access_token'])
        access_level = Teachers.get_access_level(email)

        if access_level >= Teachers.AccessLevel.ADMIN:
            return None
        else:
            return {
                'result': 'Error!',
                'error_message': 'no access'
            }

    else:
        print('error with token!')
        print(args['access_token'])
        print(status[1])
        return {
            'result': 'Error!',
            'error_message': status[1]
        }


# Получение списка учителей с их уровнями доступа
class GetTeachersApi(Resource):
    def get(self):
        # Проверяем, есть ли доступ
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p

        # Берем учителей из БД и их отправляем
        teachers = Teachers.get_all_teachers()
        return {
            "result": "OK",
            "teachers": teachers
        }


# Узнаем время между обновлениями БД
class GetUpdateTimeApi(Resource):
    def get(self):
        # Проверяем, что у пользователя есть доступ к админке
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p

        # Возвращаем данные (в часах)
        return {
            'result': "OK",
            'update_time': Metadata.UPDATE_DATABASE_PERIOD // 3600
        }


# Задаем права учителя
class SetTeacherRightsApi(Resource):
    def get(self):
        # Проверяем, что у пользователя есть доступ к админке
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)

        if std_p is not None:
            return std_p

        # Парсим параметры запроса (email и новый доступ учителя)
        parser.add_argument("email", type=str)
        parser.add_argument("access_level", type=int)

        args = parser.parse_args()

        if not args['email'] or (not args['access_level'] and args['access_level'] != 0):
            return {
                'result': 'Error!',
                'error_message': 'no required argument given!'
            }

        # Если уровень доступа подходит по формату, то задаем его, иначе кидаем ошибку
        if Teachers.AccessLevel.NO_ACCESS <= args['access_level'] <= Teachers.AccessLevel.GOD:
            Teachers.update_teachers_rights(email=args['email'], access_level=args['access_level'])
            return {
                'result': 'OK'
            }
        else:
            return {
                'result': 'Error!',
                'error_message': 'access_level should be between ' +
                                 str(Teachers.AccessLevel.NO_ACCESS) + ' and ' + str(Teachers.AccessLevel.GOD)
            }


# Читаем логи
# Внимание! Скачивание любых файлов с сервера устроено довольно костыльно:
# Почему-то при обычных (не API) запросах access_token читается некорректно
# Он как будто не обновляется(
# Поэтому для скачивания файла создается ключ доступа к этому файлу и потом пользователь переходит по ссылке,
# в которой указывает ключ доступа. Сервер проверяет подлинность ключа и отправляет файл пользователю
class ReadLogsApi(Resource):
    def get(self):
        # Проверяем, есть ли у пользователя доступ к админке
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p

        # Генерим ключ доступа для скачивания файла
        args = parser.parse_args()
        email = JWRefreshTokens.parse_email_from_token(args['access_token'])
        key = JWRefreshTokens.generate_token(email, 10)

        # Возвращаем данные (генерировать файл с логами будем потом, когда пользователь запросит скачивание)
        return {
            'result': 'OK',
            'key': str(key.encode('utf-8').hex())
        }


# Изменяем время обновления БД
class ResetUpdateTimeApi(Resource):
    def get(self):
        # Проверяем, что у пользователя есть доступ к админке
        parser = reqparse.RequestParser()
        parser.add_argument('new_update_time', type=int)
        std_p = standart_processing(parser)

        if std_p is not None:
            return std_p

        args = parser.parse_args()
        new_update_time = args['new_update_time']

        # Перезапускаем обновление БД с новыми параметрами
        if new_update_time >= Metadata.MINIMUM_UPDATE_PERIOD:
            print('restarting\n\n\n\n')
            Metadata.UPDATE_DATABASE_PERIOD = new_update_time
            update_all.restart()

            return {
                'result': 'OK'
            }
        else:
            return {
                'result': 'Error!',
                'error_message': 'new_update_time is too small!'
            }
