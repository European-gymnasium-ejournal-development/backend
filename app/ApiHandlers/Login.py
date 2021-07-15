from app.ApiHandlers import verification
from flask_restful import Api, Resource, reqparse
from flask import make_response


class Logout(Resource):
    def get(self):
        resp = make_response({'result': 'OK'})
        resp.set_cookie('access_token', "q")
        resp.set_cookie('refresh_token', "q")

        return resp


class Login(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('google_token', type=str)

        args = parser.parse_args()

        print(args['google_token'])

        result = verification.login(args['google_token'])

        print(result)

        if len(result[0]) == 0:
            return {
                'result': 'Error!',
                'error_message': 'Login failed!'
            }
        else:
            resp = make_response({'result': 'OK'})
            resp.set_cookie('access_token', result[1])
            resp.set_cookie('refresh_token', result[0])

            print(resp.status)
            print(resp.headers)
            print(resp.get_data())

            return resp
