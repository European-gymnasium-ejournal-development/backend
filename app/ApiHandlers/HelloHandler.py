from flask_restful import Api, Resource, reqparse


class HelloHandler(Resource):
    def get(self):
        print('visited')
        return {
            'message': 'Hello world!',
            'answer': 'OK'
        }

    def post(self):
        print(self)
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str)
        parser.add_argument('message', type=str)

        args = parser.parse_args()

        print(args)

        if args['message']:
            message = 'You just sent: "{}"'.format(args['message'])
            status = 'OK'
        else:
            message = 'Something went wrong!'
            status = 'ERR'

        return {'message': message, 'status': status}
