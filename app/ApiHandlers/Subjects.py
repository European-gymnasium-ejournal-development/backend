from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Subjects


# Получение предметов ученика
class SubjectsApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('student_id', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        student_id = args['student_id']

        if not student_id:
            return {
                'status': "Error!",
                'error_message': 'No student_id argument given!'
            }

        try:
            student_id = int(student_id)
        except ValueError:
            return {
                'status': 'Error!',
                'error_message': 'student_id should be integer'
            }

        if status[0]:
            subjects = Subjects.get_student_subjects(student_id)

            return {
                'result': 'OK',
                'subjects': subjects
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
