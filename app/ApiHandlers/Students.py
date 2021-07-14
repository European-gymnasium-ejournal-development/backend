from flask_restful import Resource, reqparse
from app.ApiHandlers.JWTVerification import check_access_token
from app.Database import Students


class GetStudentApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('id', type=int)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        if not args['id']:
            return {
                'result': 'Error!',
                'error_message': 'id should be given'
            }

        if status[0]:
            student = Students.get_student(args['id'])
            if student is not None:
                return {
                    'result': 'OK',
                    'student': student
                }
            else:
                return {
                    'result': 'OK',
                    'student': {}
                }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }


class StudentsApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', location='cookies', type=str)
        parser.add_argument('grade', type=str)
        parser.add_argument('part_of_name', type=str)

        args = parser.parse_args()
        status = check_access_token(args['access_token'])

        part_of_name = args['part_of_name'] if args['part_of_name'] else ""
        grade = args['grade']

        if not grade:
            return {
                'status': 'Error!',
                'error_message': "No grade argument given!"
            }

        if status[0]:
            students = Students.get_all_students_of_grade(grade, part_of_name=part_of_name)

            return {
                'result': 'OK',
                'students': students
            }
        else:
            return {
                'result': 'Error!',
                'error_message': status[1]
            }
