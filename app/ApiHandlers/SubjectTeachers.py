from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Subjects


class SubjectTeachersApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('subject_id', type=int)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        if not args['subject_id']:
            return {
                'result': 'Error!',
                'error_message': 'no required argument given'
            }

        if status[0]:
            teachers = Subjects.get_subjects_teachers(args['subject_id'])

            return {
                'result': 'OK',
                'grades': teachers
            }
        else:
            print('error with token!')
            print(args['access_token'])
            print(status[1])
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
