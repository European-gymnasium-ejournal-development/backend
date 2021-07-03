from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import JWRefreshTokens
import datetime


class LogsApi(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('action', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        if status[0] and args['action']:
            ip = reqparse.request.remote_addr
            email = JWRefreshTokens.parse_email_from_token(args['access_token'])
            action = args['action']
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            # TODO: добавить логирование в какой-то файл

        return {}

