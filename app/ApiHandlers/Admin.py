from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Teachers, JWRefreshTokens
from config import Metadata
from ManageBackApi import update_all
import os
import sys
from flask import send_file, redirect
import datetime


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


class GetTeachersApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p

        teachers = Teachers.get_all_teachers()
        return {
            "result": "OK",
            "teachers": teachers
        }


class GetUpdateTimeApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p
        return {
            'result': "OK",
            'update_time': Metadata.UPDATE_DATABASE_PERIOD // 3600
        }


class SetTeacherRightsApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)

        if std_p is not None:
            return std_p

        parser.add_argument("email", type=str)
        parser.add_argument("access_level", type=int)

        args = parser.parse_args()

        if not args['email'] or (not args['access_level'] and args['access_level'] != 0):
            return {
                'result': 'Error!',
                'error_message': 'no required argument given!'
            }

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


class ReadLogsApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        std_p = standart_processing(parser)
        if std_p is not None:
            return std_p

        args = parser.parse_args()
        email = JWRefreshTokens.parse_email_from_token(args['access_token'])
        key = JWRefreshTokens.generate_token(email, 10)
        return {
            'result': 'OK',
            'key': key
        }


class ResetUpdateTimeApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('new_update_time', type=int)
        std_p = standart_processing(parser)

        if std_p is not None:
            return std_p

        args = parser.parse_args()
        new_update_time = args['new_update_time']

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
