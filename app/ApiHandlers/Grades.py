from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students


class GradesApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])
        if status[0]:
            grades_list = Students.get_all_grades()

            return {
                'result': 'OK',
                'grades': grades_list
            }
        else:
            print('error with token!')
            print(args['access_token'])
            print(status[1])
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
