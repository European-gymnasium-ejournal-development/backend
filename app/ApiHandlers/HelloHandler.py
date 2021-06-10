from flask_restful import Api, Resource, reqparse
from app.ApiHandlers.verification import parse_token


class HelloHandler(Resource):
    def get(self):
        print(self)
        print('visited')
        return {
            'message': 'Hello world!',
            'answer': 'OK'
        }

    def post(self):
        print(self)
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str)

        args = parser.parse_args()

        print(args)

        if parse_token(args['token']):
            print('visited')
            return {
                'message': 'Hello world!',
                'answer': 'OK'
            }
        else:
            print('problem with token')
            return {
                'message': 'Error! Problem with token',
                'answer': 'Error!'
            }
