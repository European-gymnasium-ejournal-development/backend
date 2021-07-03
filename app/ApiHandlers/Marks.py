from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Marks


class MarksApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)

        expected_args = ['student_id', 'time_from', 'time_to', 'subject_id']

        for arg in expected_args:
            parser.add_argument(arg, type=str)

        args = parser.parse_args()

        for arg in expected_args:
            if not args[arg]:
                return {
                    'status': 'Error!',
                    'error_message': 'No {} argument given!'.format(arg)
                }

        try:
            args['student_id'] = int(args['student_id'])
        except ValueError:
            return {
                'status': 'Error!',
                'error_message': 'student_id should be integer'
            }

        try:
            args['subject_id'] = int(args['subject_id'])
        except ValueError:
            return {
                'status': 'Error!',
                'error_message': 'subject_id should be integer'
            }

        status = check_access_token(args['access_token'])
        if status[0]:
            marks_list = Marks.get_marks(student_id=args['student_id'], time_from=args['time_from'],
                                         time_to=args['time_to'], subject_id=args['subject_id'])

            return {
                'result': 'OK',
                'marks': marks_list
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
