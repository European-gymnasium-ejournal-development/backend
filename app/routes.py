from app import app, api
from flask import send_from_directory
from app.ApiHandlers import HelloHandler, Login, RefreshToken, Grades, Logs, Marks, Students, Subjects, Admin


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/main')
def main():
    return serve_index()


@app.route('/admin')
def admin():
    return serve_index()


@app.route('/export')
def export():
    return serve_index()


api.add_resource(HelloHandler.HelloHandler, '/api/hello')
api.add_resource(Login.Login, '/api/login')
api.add_resource(RefreshToken.RefreshToken, '/api/refresh_token')
api.add_resource(Grades.GradesApi, '/api/grades')
api.add_resource(Marks.MarksApi, '/api/marks')
api.add_resource(Students.StudentsApi, '/api/students')
api.add_resource(Subjects.SubjectsApi, '/api/subjects')
api.add_resource(Logs.LogsApi, '/api/logs')
api.add_resource(Admin.GetUpdateTimeApi, '/api/update_time')
api.add_resource(Admin.ResetUpdateTimeApi, '/api/reset_update_time')
api.add_resource(Admin.ReadLogsApi, '/api/read_logs')
api.add_resource(Admin.SetTeacherRightsApi, '/api/reset_rights')
api.add_resource(Admin.GetTeachersApi, '/api/get_teachers')
