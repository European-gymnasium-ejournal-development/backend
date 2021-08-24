from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from create.config import Metadata


# Получение всех классов, которые есть в системе
class LastUpdateApi(Resource):
    def get(self):
        return {
            'result': 'OK',
            'last_update': Metadata.LAST_UPDATE.strftime("%d.%m.%Y %H:%M:%S")
        }

