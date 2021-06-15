from app.ApiHandlers import verification
from flask_restful import Api, Resource, reqparse


class Login(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('google_token', type=str)

        args = parser.parse_args()

        print(args['google_token'])

        result = verification.login(args['google_token'])

        if len(result[0]) == 0:
            return {
                'result': 'Error!',
                'error_message': 'Login failed!'
            }
        else:
            return {
                'result': 'OK',
                'refresh_token': result[0],
                'access_token': result[1]
            }
